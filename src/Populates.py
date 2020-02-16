from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Bookables, Base

engine = create_engine('sqlite:///books-collection.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object.
session = DBSession()

user = User(name='hassan')
booakble = Bookables(name="bookable1", user_id=1, details="asdasdasd")
# To persist our ClassName object, we add() it to our Session:
session.add(user)
session.add(booakble)
# To issue the changes to our database and commit the transaction we use commit(). #Any change made against the objects in the session won't be persisted into the #database until you call session.commit().

session.commit()
