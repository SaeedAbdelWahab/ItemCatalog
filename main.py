from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item, User
import os

engine = create_engine('sqlite:///CatalogApp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)

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
			session['logged_in'] = True
			return redirect(url_for('catalogHome'))
		else:
			flash('Wrong Credintials !')
			return render_template('login.html')
	else :
		return render_template('login.html')

@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('catalogHome'))


@app.route('/')
def catalogHome():
	dbsession = DBSession()
	categories = dbsession.query(Category)
	items = dbsession.query(Item).order_by(desc('id')).limit(5)
	dictionary = dict([(key.name, []) for key in items])
	for i in range(5) :
		dictionary[items[i].name] = dbsession.query(Category).filter_by(id = items[i].category_id).one()
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
			print ("im hereee")
			categoryName = request.form['categoryName']
			print (categoryName)
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


if __name__ == '__main__':
    app.debug = True
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=8000)