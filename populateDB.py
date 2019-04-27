from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item, User

engine = create_engine('sqlite:///CatalogApp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

dbsession = DBSession()

user = User(username="admin")
user.password = user.hash_password("admin")
dbsession.add(user)
dbsession.commit()

cat = Category(name="Soccer")
dbsession.add(cat)
dbsession.commit()
newItem = Item(name="Ball",
               category_id=cat.id,
               description="A round and black object")
dbsession.add(newItem)
dbsession.commit()
newItem = Item(name="Pitch",
               category_id=cat.id,
               description="A vast area for playing")
dbsession.add(newItem)
dbsession.commit()
newItem = Item(name="Shoes",
               category_id=cat.id,
               description="An item wore in feet to facilitate running")
dbsession.add(newItem)
dbsession.commit()

cat = Category(name="Swimming")
dbsession.add(cat)
dbsession.commit()
newItem = Item(name="Swimsuit",
               category_id=cat.id,
               description="An item wore for swimming")
dbsession.add(newItem)
dbsession.commit()
newItem = Item(name="Board",
               category_id=cat.id,
               description="An item used for swimming")
dbsession.add(newItem)
dbsession.commit()
cat = Category(name="Hunting")
dbsession.add(cat)
dbsession.commit()
cat = Category(name="Surfing")
dbsession.add(cat)
dbsession.commit()
cat = Category(name="Boxing")
dbsession.add(cat)
dbsession.commit()


