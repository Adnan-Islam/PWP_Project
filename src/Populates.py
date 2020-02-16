import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import User, Bookables, Slot, Base


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def insert_objects(arrray_of_objects, session):
    # To persist our ClassName object, we add() it to our Session:
    session.add_all(arrray_of_objects)
    # To issue the changes to our database and commit the transaction we use commit(). #Any change made against the objects in the session won't be persisted into the #database until you call session.commit().
    session.commit()


def create_dummy_users():
    users = [User(name='hassan'), User(name="Berk"), User(name="Adnan")]
    return users


def create_dummy_bookables():
    booakbles = [Bookables(name="bookable2", user_id=1, details="gggg"), Bookables(
        name="bookable4", user_id=2, details="dgdg"), Bookables(name="bk2", user_id=1, details="dsdsa")]
    return booakbles


def create_dummy_slots():
    slots = [Slot(booakble_id=1, ending_time=datetime.datetime(2020, 3, 1), availability=True, owner_id=1, client_id=2), Slot(
        booakble_id=3, ending_time=datetime.datetime(2020, 6, 15), availability=True, owner_id=1, client_id=2)]
    return slots


engine = create_engine('sqlite:///books-collection.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object.
session = DBSession()

users = create_dummy_users()
bookables = create_dummy_bookables()
slots = create_dummy_slots()

insert_objects(users, session)
insert_objects(bookables, session)
insert_objects(slots, session)
