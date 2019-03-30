from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item
app = Flask(__name__)

engine = create_engine('sqlite:///CatalogApp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


@app.route('/')
def catalogHome():
	session = DBSession()
	categories = session.query(Category)
	return render_template('index.html', categories=categories)

@app.route('/catalog/<string:categoryName>')
def categoryItems(categoryName):
	session = DBSession()
	category = session.query(Category).filter_by(name=categoryName).first() 
	items = session.query(Item).filter_by(category_id=category.id)
	return render_template('category.html', items = items, category = category)

@app.route('/catalog/<string:categoryName>/new', methods=['GET','POST'])
def addItem(categoryName):
	if request.method == 'POST':
		session = DBSession()
		category = session.query(Category).filter_by(name=categoryName).first()
		newItem = Item(
			name=request.form['name'], category_id=category.id, description = request.form['description'])
		session.add(newItem)
		session.commit()
		return redirect(url_for('categoryItems', categoryName=categoryName))
	else :
		return render_template('newItem.html', categoryName = categoryName)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)