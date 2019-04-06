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
cat = Category(name="Swimming")
dbsession.add(cat)
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


