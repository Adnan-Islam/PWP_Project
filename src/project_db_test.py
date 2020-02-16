import os
import pytest
import tempfile
import datetime
import app
from app import User, Bookables, Slot, BookRequest, ResourceLink
#from models.models import User, Bookables, Slot, Base, BookRequest, ResourceLink
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    """This is for setting up a fresh database for testing and providing session to that database to the test functions"""
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db
    
    app.db.session.remove()
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
        starting_time=datetime.datetime(2020, 3, 1),
        ending_time=datetime.datetime(2020, 5, 2),
        availability=True
    )

def _get_book_request():
    """Creates a dummy BookRequest instance"""
    return BookRequest()

def test_create_instances_and_relationships(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
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
    
def test_update_instances(db_handle):    
    """
    Tests that we can retrieve an instance of each model and update them.
    """
    
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
   
   
   
    # Retrieve objects
    db_user = User.query.first()
    db_bookable = Bookables.query.first()
    db_slot = Slot.query.first()
    db_bookrequest = BookRequest.query.first()
    db_resourcelink = ResourceLink.query.first()
    
    #update objects
    db_user.name="updatedname"
    db_bookable.name="updatedname"
    db_slot.ending_time=datetime.datetime(2040, 4, 4)
    db_bookrequest.approved = True
    db_resourcelink.url = "updatedurl"
    
    #update changes
    db_handle.session.commit()
    
    #check for integrities
    assert User.query.first().name == "updatedname"
    assert Bookables.query.first().name == "updatedname"
    assert Slot.query.first().ending_time == datetime.datetime(2040, 4, 4)
    assert BookRequest.query.first().approved == True 
    assert ResourceLink.query.first().url == "updatedurl"
 
def test_deleting_user(db_handle):   
    """
    Tests that when we remove a user all dependent rows will be removed.
    """
    
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
    #start testing
    db_handle.session.delete(user)
    db_handle.session.commit()
    
    assert User.query.count() == 1 #only user2 is remaining
    assert Bookables.query.count() == 0
    assert Slot.query.count() == 0
    assert BookRequest.query.count() == 0
    assert ResourceLink.query.count() == 0

def test_deleting_bookable(db_handle):  
    """
    Tests that when we remove a bookable all dependent rows will be removed.
    """
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
    #start testing
    db_handle.session.delete(bookable)
    db_handle.session.commit()
    
    assert User.query.count() == 2 
    assert Bookables.query.count() == 0
    assert Slot.query.count() == 0
    assert BookRequest.query.count() == 0
    assert ResourceLink.query.count() == 0
    
def test_deleting_slot(db_handle):  
    """
    Tests that when we remove a slot all dependent rows will be removed.
    """
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
    #start testing
    db_handle.session.delete(slot)
    db_handle.session.commit()
    
    assert User.query.count() == 2 
    assert Bookables.query.count() == 1
    assert Slot.query.count() == 0
    assert BookRequest.query.count() == 0
    assert ResourceLink.query.count() == 1
    
def test_deleting_book_request(db_handle):  
    """
    Tests that when we remove a BookRequest all dependent rows will be removed.
    """
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
    #start testing
    db_handle.session.delete(bookrequest)
    db_handle.session.commit()
    
    assert User.query.count() == 2 
    assert Bookables.query.count() == 1
    assert Slot.query.count() == 1
    assert BookRequest.query.count() == 0
    assert ResourceLink.query.count() == 1
    
def test_deleting_resource_link(db_handle):  
    """
    Tests that when we remove a ResourceLink all dependent rows will be removed.
    """
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
    db_handle.session.add(user)
    db_handle.session.add(user2)
    db_handle.session.add(bookable)
    db_handle.session.add(resourcelink)
    db_handle.session.add(slot)
    db_handle.session.add(bookrequest)
    db_handle.session.commit()
    
    #start testing
    db_handle.session.delete(resourcelink)
    db_handle.session.commit()
    
    assert User.query.count() == 2 
    assert Bookables.query.count() == 1
    assert Slot.query.count() == 1
    assert BookRequest.query.count() == 1
    assert ResourceLink.query.count() == 0