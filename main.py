from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item
app = Flask(__name__)

engine = create_engine('sqlite:///CatalogApp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def catalogHome():
	categories = session.query(Category)

	return render_template('index.html', categories=categories)


    # items = session.query(Item).filter_by(category_id=category.id)
    # output = ''
    # for i in items:
    #     output += i.name
    #     output += '</br>'
    # return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)