import json
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from bookingapi.utils import LINK_RELATIONS_URL
from bookingapi import create_app, db
from bookingapi.models import User, Bookables, Slot



@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        _populate_db()
        
    yield app.test_client()
    
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
     # Create everything
    user = User(
        name="user1"
    )
    user2 = User(
        name="user2"
    )
    bookable = Bookables(
        name="test bookable",
        details="Planet Earth"
    )
    slot = Slot(
        starting_time=datetime(2020, 3, 1),
        ending_time=datetime(2020, 5, 2),
        availability=True
    )
    
    #Form relations
    bookable.user = user
    slot.owner = user
    slot.client = user2
    slot.bookable = bookable
    
    #add to database
    db.session.add(user)
    db.session.add(user2)
    db.session.add(bookable)
    db.session.add(slot)
    db.session.commit()

def _get_user_json(uname="testuser"):
    """Creates a dummy User instance"""
    return {"name": uname}
    

def _get_bookable_json():
    """Creates a dummy Bookable instance"""
    return {"name": "hello_user", "details":"Planet Earth"}

def _get_slot_json():
    """Creates a dummy Slot instance"""
    return {
        "starting_time": "{}".format(datetime(2020, 3, 1)),
        "ending_time": "{}".format(datetime(2020, 5, 2)),
        "availability": True
    }
     
def _check_namespace(client, response):
    """
    Checks that the "bookingmeta" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    
    ns_href = response["@namespaces"]["bookingmeta"]["name"]
    assert ns_href == LINK_RELATIONS_URL
    
def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200
    
def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204
    
def _check_control_put_method(ctrl, client, obj, data_provider):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = data_provider()
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_sensor_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestUserCollection(object):
    """
    This class implements tests for POST HTTP method in user collection
    resource. 
    """
    
    RESOURCE_URL = "/api/users/"

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_user_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #test with wrong data types
        
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"]
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "testuser"
        
        # remove model field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestUserItem(object):
    
    RESOURCE_URL = "/api/users/1/"
    INVALID_URL = "/api/users/9999d/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "user1"
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("bookingmeta:all-bookables", client, body)
        _check_control_get_method("bookingmeta:bookables-by", client, body)
        _check_control_put_method("edit", client, body, _get_user_json)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the user can be found from its new URI. 
        """
        
        valid = _get_user_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with valid (only change name)
        valid["name"] = "test-user-edited"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        
    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestBookableCollection(object):
    """
    This class implements tests for each HTTP method in BookableCollection
    resource. 
    """
    
    RESOURCE_URL = "/api/users/1/bookables/"
    INVALID_URL = "/api/users/99999/bookables/"
    

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        #invalid user
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
        
        #correct request
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            assert "name" in item
            assert "details" in item


class TestBookableCollectionofUser(object):
    """
    This class implements tests for each HTTP method in BookableCollectionofUser
    resource. 
    """
    
    RESOURCE_URL = "/api/users/1/my_bookables/"
    INVALID_URL = "/api/users/9999/my_bookables/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            assert "name" in item
            assert "details" in item
        
        #invalid user
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_bookable_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #non existing user
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"]
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "hello_user"
        assert body["details"] == "Planet Earth"
        # remove name field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestBookableItemofUser(object):
    
    RESOURCE_URL = "/api/users/1/my_bookables/1/"
    INVALID_USER = "/api/users/6999999/my_bookables/555555/"
    INVALID_BOOKABLE = "/api/users/1/my_bookables/555555/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "test bookable"
        assert body["details"] == "Planet Earth"
        _check_namespace(client, body)
        #invalid user
        resp = client.get(self.INVALID_USER)
        assert resp.status_code == 404
        #invalid bookable
        resp = client.get(self.INVALID_BOOKABLE)
        assert resp.status_code == 404
        
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the user can be found from its new URI. 
        """
        
        valid = _get_bookable_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_USER, json=valid)
        assert resp.status_code == 404
        
        # test with valid (only change name)
        valid["name"] = "test-bookable-edited"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        
    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_USER)
        assert resp.status_code == 404


class TestSlotCollectionofUser(object):

    """
    This class implements tests for each HTTP method in BookableCollectionofUser
    resource. 
    """
    
    RESOURCE_URL = "/api/users/1/my_bookables/1/slots/"
    INVALID_USER = "/api/users/9999/my_bookables/1/slots/"
    INVALID_BOOKABLE = "/api/users/1/my_bookables/99999/slots/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            assert "starting_time" in item
            assert "ending_time" in item
            assert "availability" in item
        
        #invalid user
        resp = client.get(self.INVALID_USER)
        assert resp.status_code == 404
        
        #invalid bookable
        resp = client.get(self.INVALID_BOOKABLE)
        assert resp.status_code == 404

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_slot_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #non existing user
        resp = client.post(self.INVALID_USER, json=valid)
        assert resp.status_code == 404
        
        #non existing bookable
        resp = client.post(self.INVALID_BOOKABLE, json=valid)
        assert resp.status_code == 404
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"]
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["starting_time"]
        assert body["ending_time"]
        assert body["availability"] == True
        
        # remove name field for 400
        valid.pop("starting_time")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestSlotItemofUser(object):
    
    RESOURCE_URL = "/api/users/1/my_bookables/1/slots/1/"
    INVALID_USER = "/api/users/6999999/my_bookables/555555/slots/1/"
    INVALID_BOOKABLE = "/api/users/1/my_bookables/555555/slots/1/"
    INVALID_SLOT = "/api/users/1/my_bookables/1/slots/15523123/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["starting_time"] == "{}".format(datetime(2020, 3, 1))
        assert body["ending_time"] == "{}".format(datetime(2020, 5, 2))
        assert body["availability"] == True
        _check_namespace(client, body)
        
        #invalid user
        resp = client.get(self.INVALID_USER)
        assert resp.status_code == 404
        #invalid bookable
        resp = client.get(self.INVALID_BOOKABLE)
        assert resp.status_code == 404
        #invalid slot
        resp = client.get(self.INVALID_SLOT)
        assert resp.status_code == 404
        
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the user can be found from its new URI. 
        """
        
        valid = _get_slot_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #invalid user
        resp = client.put(self.INVALID_USER, json=valid)
        assert resp.status_code == 404
        #invalid bookable
        resp = client.put(self.INVALID_BOOKABLE, json=valid)
        assert resp.status_code == 404
        #invalid slot
        resp = client.put(self.INVALID_SLOT, json=valid)
        assert resp.status_code == 404
        
        # test with valid (only change availability)
        valid["availability"] = False
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("starting_time")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        
    def test_delete(self, client):
        #delete resource
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        #check if deleted
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        #invalid user
        resp = client.delete(self.INVALID_USER)
        assert resp.status_code == 404
        #invalid bookable
        resp = client.delete(self.INVALID_BOOKABLE)
        assert resp.status_code == 404
        #invalid slot
        resp = client.delete(self.INVALID_SLOT)
        assert resp.status_code == 404
