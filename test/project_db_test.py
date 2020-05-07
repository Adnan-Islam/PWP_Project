import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from bookingapi import create_app, db
from bookingapi.models import User, Bookables, Slot, ResourceLink, BookRequest

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_user(uname):
    """Creates a dummy User instance"""
    return User(
        name=uname
    )


def _get_bookable():
    """Creates a dummy Bookable instance"""
    return Bookables(
        name="hello_user",
        details="I am from Earth"
    )

def _get_resource_link():
    """Creates a dummy ResourceLink instance"""
    return ResourceLink(
        url="Mr.Google"
    )

def _get_slot():
    """Creates a dummy Slot instance"""
    return Slot(
        starting_time = "2020-05-01 00:00:00",
        ending_time = "2020-05-02 00:00:00",
        availability=True
    )

def _get_book_request():
    """Creates a dummy BookRequest instance"""
    return BookRequest()

def test_create_instances_and_relationships(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        # Check that everything exists
        assert User.query.count() == 2
        assert Bookables.query.count() == 1
        assert Slot.query.count() == 1
        assert BookRequest.query.count() == 1
        assert ResourceLink.query.count() == 1
       
        # Prepare for the next step
        db_user = User.query.all()[0]
        db_user2 = User.query.all()[1]
        db_bookable = Bookables.query.first()
        db_slot = Slot.query.first()
        db_bookrequest = BookRequest.query.first()
        db_resourcelink = ResourceLink.query.first()
        
        # Check all relationships (both sides)
        assert db_bookable.user == db_user
        assert db_slot.bookable == db_bookable
        assert db_slot.owner == db_user
        assert db_slot.client == db_user2
        assert db_resourcelink.bookable == db_bookable
        assert db_bookrequest.slot == db_slot
        assert db_bookrequest.sender == db_user2
        assert db_bookrequest.receiver == db_user
        
        assert db_bookable in db_user.bookables
        assert db_slot in db_bookable.slots
        assert db_slot in db_user.slot_owner
        assert db_slot in db_user2.slot_client
        assert db_resourcelink in db_bookable.resource_links    
        assert db_bookrequest in db_slot.book_requests    
        assert db_bookrequest in db_user2.book_request_sender    
        assert db_bookrequest in db_user.book_request_receiver    
    
def test_update_instances(app):    
    """
    Tests that we can retrieve an instance of each model and update them.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
       
       
       
        # Retrieve objects
        db_user = User.query.first()
        db_bookable = Bookables.query.first()
        db_slot = Slot.query.first()
        db_bookrequest = BookRequest.query.first()
        db_resourcelink = ResourceLink.query.first()
        
        #update objects
        db_user.name="updatedname"
        db_bookable.name="updatedname"
        db_slot.ending_time=str(datetime(2040, 4, 4))
        db_bookrequest.approved = True
        db_resourcelink.url = "updatedurl"
        
        #update changes
        db.session.commit()
        
        #check for integrities
        assert User.query.first().name == "updatedname"
        assert Bookables.query.first().name == "updatedname"
        assert Slot.query.first().ending_time == str(datetime(2040, 4, 4))
        assert BookRequest.query.first().approved == True 
        assert ResourceLink.query.first().url == "updatedurl"
 
def test_deleting_user(app):   
    """
    Tests that when we remove a user all dependent rows will be removed.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        #start testing
        db.session.delete(user)
        db.session.commit()
        
        assert User.query.count() == 1 #only user2 is remaining
        assert Bookables.query.count() == 0
        assert Slot.query.count() == 0
        assert BookRequest.query.count() == 0
        assert ResourceLink.query.count() == 0

def test_deleting_bookable(app):  
    """
    Tests that when we remove a bookable all dependent rows will be removed.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        #start testing
        db.session.delete(bookable)
        db.session.commit()
        
        assert User.query.count() == 2 
        assert Bookables.query.count() == 0
        assert Slot.query.count() == 0
        assert BookRequest.query.count() == 0
        assert ResourceLink.query.count() == 0
    
def test_deleting_slot(app):  
    """
    Tests that when we remove a slot all dependent rows will be removed.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        #start testing
        db.session.delete(slot)
        db.session.commit()
        
        assert User.query.count() == 2 
        assert Bookables.query.count() == 1
        assert Slot.query.count() == 0
        assert BookRequest.query.count() == 0
        assert ResourceLink.query.count() == 1
    
def test_deleting_book_request(app):  
    """
    Tests that when we remove a BookRequest all dependent rows will be removed.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        #start testing
        db.session.delete(bookrequest)
        db.session.commit()
        
        assert User.query.count() == 2 
        assert Bookables.query.count() == 1
        assert Slot.query.count() == 1
        assert BookRequest.query.count() == 0
        assert ResourceLink.query.count() == 1
    
def test_deleting_resource_link(app):  
    """
    Tests that when we remove a ResourceLink all dependent rows will be removed.
    """
    with app.app_context():
        # Create everything
        user = _get_user("user1")
        user2 = _get_user("user2")
        bookable = _get_bookable()
        resourcelink = _get_resource_link()
        slot = _get_slot()
        bookrequest = _get_book_request()
        
        #Form relations
        bookable.user = user
        slot.owner = user
        slot.client = user2
        slot.bookable = bookable
        resourcelink.bookable = bookable
        bookrequest.slot = slot
        bookrequest.sender = user2
        bookrequest.receiver = user
        
        #add to database
        db.session.add(user)
        db.session.add(user2)
        db.session.add(bookable)
        db.session.add(resourcelink)
        db.session.add(slot)
        db.session.add(bookrequest)
        db.session.commit()
        
        #start testing
        db.session.delete(resourcelink)
        db.session.commit()
        
        assert User.query.count() == 2 
        assert Bookables.query.count() == 1
        assert Slot.query.count() == 1
        assert BookRequest.query.count() == 1
        assert ResourceLink.query.count() == 0