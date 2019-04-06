from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item, User
import os
import random
import string
from collections import OrderedDict 

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


engine = create_engine('sqlite:///CatalogApp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)


CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"



def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        return
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		print ("here")
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = session.get('access_token')
	stored_gplus_id = session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	session['access_token'] = credentials.access_token
	session['gplus_id'] = gplus_id
	session ['logged_in'] = True

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	session['username'] = data['name']
	
	return redirect(url_for('catalogHome'))

def verify_password(username, password):
	dbsession = DBSession()
	user = dbsession.query(User).filter_by(username = username).first()
	if not user or not user.verify_password(password):
		return False
	return True

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method == 'POST' :
		username = request.form['username']
		password = request.form['password']
		if verify_password(username, password):
			session['username'] = username 
			session['logged_in'] = True

			return redirect(url_for('catalogHome'))
		else:
			flash('Wrong Credintials !')
			return render_template('login.html')
	else :
			state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
			session['state'] = state
			return render_template('login.html',STATE = state)

@app.route('/logout')
def logout():
	session['logged_in'] = False
	gdisconnect()
	return redirect(url_for('catalogHome'))


@app.route('/')
def catalogHome():
	dbsession = DBSession()
	categories = dbsession.query(Category)
	items = dbsession.query(Item).order_by(desc('time_created')).limit(5)
	dictionary = OrderedDict() 
	for i in range(5) :
		dictionary[items[i].name] = dbsession.query(Category).filter_by(id = items[i].category_id).first()
	return render_template('index.html', categories=categories, items = dictionary)

@app.route('/catalog/<string:categoryName>')
def categoryItems(categoryName):
	dbsession = DBSession()
	category = dbsession.query(Category).filter_by(name=categoryName).first() 
	items = dbsession.query(Item).filter_by(category_id=category.id)
	return render_template('category.html', items = items, category = category)

@app.route('/catalog/<string:categoryName>/<string:itemName>')
def getItem(categoryName, itemName):
	dbsession = DBSession()
	category = dbsession.query(Category).filter_by(name=categoryName).first() 
	item = dbsession.query(Item).filter_by(name = itemName, category_id = category.id).first()
	return render_template('item.html', item = item, category = category)

@app.route('/catalog/<string:categoryName>/new', methods=['GET','POST'])
def addItem(categoryName = ""):
	dbsession = DBSession()
	if session['logged_in'] :
		if request.method == 'POST':
			categoryName = request.form['categoryName']
			category = dbsession.query(Category).filter_by(name=categoryName).first()
			newItem = Item(
				name=request.form['name'], category_id=category.id, description = request.form['description'])
			dbsession.add(newItem)
			dbsession.commit()
			return redirect(url_for('categoryItems', categoryName=categoryName))
		else :
			categories = dbsession.query(Category).all();
			return render_template('newItem.html', categoryName = categoryName, categories = categories)
	else :
		return render_template('loginWarning.html')

@app.route('/catalog/<string:categoryName>/<string:itemName>/edit',
		   methods=['GET', 'POST'])
def editItem(categoryName, itemName):
	if session['logged_in'] :
		dbsession = DBSession()
		category = dbsession.query(Category).filter_by(name=categoryName).first()
		editedItem = dbsession.query(Item).filter_by(name=itemName, category_id = category.id).first()
		if request.method == 'POST':
			if request.form['name']:
				editedItem.name = request.form['name']
			if request.form['description']:
				editedItem.description = request.form['description']
			dbsession.add(editedItem)
			dbsession.commit()
			return redirect(url_for('categoryItems', categoryName = categoryName))
		else:
			return render_template(
				'editedItem.html', category = category, item = editedItem)
	else :
		return render_template('loginWarning.html')



@app.route('/catalog/<string:categoryName>/<string:itemName>/delete',
		   methods=['GET', 'POST'])
def deleteItem(categoryName, itemName):
	if session['logged_in'] :
		dbsession = DBSession()
		category = dbsession.query(Category).filter_by(name=categoryName).first()
		itemToDelete = dbsession.query(Item).filter_by(name=itemName, category_id = category.id).first()
		if request.method == 'POST':
			dbsession.delete(itemToDelete)
			dbsession.commit()
			return redirect(url_for('categoryItems', categoryName = categoryName))
		else:
			return render_template('deletedItem.html',category = category,  item=itemToDelete)
	else :
		return render_template('loginWarning.html')

@app.route('/catalog.json')
def getData() :
	dbsession = DBSession()
	categories = dbsession.query(Category).all()
	serializedCategories = [i.serialize for i in categories]
	items = dbsession.query(Item).all()
	serializedItems = [i.serialize for i in items]
	for item in serializedItems :
		for category in serializedCategories :
			if item['category_id'] == category['id'] :
				category['items'].append(item)
	return jsonify(Categories= serializedCategories)

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'super_secret_key'
	app.run(host='0.0.0.0', port=8000)