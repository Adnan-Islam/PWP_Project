from models.models import User, Base, Bookables, Slot
from api import APIInitializer
from utils import MasonBuilder, Utils, UserItemBuilder, BookableBuilder, LINK_RELATIONS_URL, MASON
from flask_restful import Resource
from flask import Flask, request,  abort, Response
from sqlalchemy import create_engine, update, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event, exc
import json
import os
import sys
import inspect
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


engine = create_engine('sqlite:///books-collection.db',
                       connect_args={'check_same_thread': False})
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object.
session = DBSession()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# ##########################################
# ##########################################
#Resources
# ##########################################
#Exceptions
# KeyError and ValueError are thrown when the reqeuest is json but the keys or values in the request are not as the same as server expected 
# TypeError is thrown when the request is not json

class UserCollection(Resource):
    def post(self):
        #Check if the request is in the right form
        if request.is_json:
            try:
                #Creating new user
                new_user = [User(name=request.json['name'])]
                session.add_all(new_user)
                #commiting the changes
                session.commit()
                return None, 201
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request,'name'is string", path=request.path
                                                   )
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class UserItem(Resource):
    def get(self, userID):
        try:
            #query the user based on the ID
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            #getting a instance of our api which consists of resources' routes
            singelton = APIInitializer.getInstance()
            body = UserItemBuilder(id=user.id, name=user.name)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", request.path)
            body.add_control_add_user(
                singelton.get_api().url_for(UserCollection))
            body.add_control_edit_user(
                userID, singelton.get_api().url_for(UserItem, userID=userID))
            body.add_control_delete_user(
                userID, singelton.get_api().url_for(UserItem, userID=userID))
            # body.add_control_get_all_bookables(userId,api.url_for))
            body.add_control_get_bookables_by(userID=userID, url=singelton.get_api(
            ).url_for(BooakbleCollectionofUser, userID=userID))
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            pass

    def put(self, userID):
        #Check if the request is in the right form
        if request.json:
            try:
                new_name = request.json["name"]
                #query the user based on the ID
                user = session.query(User).filter_by(id=userID).first()
                if new_name is None or user is None:
                    raise ValueError()

                user.name = new_name
                session.commit()
                return None, 204
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request,'name'is string", path=request.path
                                                   )
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID):
        try:
            #query the user based on the ID
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            session.query(User).filter_by(id=userID).delete()
            session.commit()

            return None, 204
        except (KeyError, ValueError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no attribute 'name' found in the request,'name'is string", path=request.path
                                               )


class BooakbleCollectionofUser(Resource):
    def get(self, userID):
        try:
            #query the user based on the ID
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            bookables = session.query(Bookables).filter_by(user_id=userID)
            #getting a instance of our api which consists of resources' routes
            singelton = APIInitializer.getInstance()
            body = BookableBuilder(items=[])
            for i in bookables:
                item = MasonBuilder(name=i.name, details=i.details)
                item.add_control("self", singelton.get_api().url_for(
                    BooakbleCollectionofUser, userID=userID))
                item.add_control("profile", href="/profiles/Bookable/")
                body["items"].append(item)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", singelton.get_api().url_for(
                BooakbleCollectionofUser, userID=userID))
            body.add_control_add_bookable(userID=userID, url=singelton.get_api().url_for(
                BooakbleCollectionofUser, userID=userID))
            body.add_control_user(url=singelton.get_api().url_for(
                UserItem, userID=userID))
            return Response(json.dumps(body), 200, mimetype=MASON)

        except (KeyError, ValueError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no attribute 'name' found in the request,'name'is string", path=request.path
                                               )

    def post(self, userID):
        if request.is_json:
            try:
                user = session.query(User).filter_by(id=userID).first()
                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                       message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                       )
                bookables = [Bookables(
                    name=request.json['name'], details=request.json['details'], user_id=userID)]
                session.add_all(bookables)
                session.commit()
                return None, 201
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request, name is string", path=request.path
                                                   )

        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class BookableItemofUser(Resource):
    def get(self, userID, bookableID):
        try:
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            bookable_item = session.query(Bookables).filter_by(
                user_id=userID, id=bookableID).first()
            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a bookable item ==> ID={}".format(bookableID), path=request.path
                                                   )
            #getting a instance of our api which consists of resources' routes
            singelton = APIInitializer.getInstance()
            body = BookableBuilder(
                id=bookableID, user_id=userID, name=bookable_item.name, details=bookable_item.details)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", request.path)
            body.add_control_user(
                singelton.get_api().url_for(UserCollection))
            body.add_control_slots_of(userID=userID, bookableID=bookableID,
                                      url=singelton.get_api().url_for(UserItem, userID=userID))
            body.add_control_edit(userID=userID, bookableID=bookableID,
                                  url=request.path)
            body.add_control_delete(
                userID=userID, bookableID=bookableID, url=request.path)
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            pass

    def put(self, userID, bookableID):
        if request.json:
            try:
                new_name = request.json["name"]
                new_details = request.json['details']
                user = session.query(User).filter_by(id=userID).first()
                bookable_item = session.query(Bookables).filter_by(
                    user_id=userID, id=bookableID).first()
                if new_name is None or new_details is None:
                    raise ValueError()

                bookable_item.name = new_name
                bookable_item.details = new_details
                session.commit()
                return None, 204
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' or 'details' found in the request,'name' and 'details' are string", path=request.path
                                                   )
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID, bookableID):
        try:
            bookable_item = session.query(Bookables).filter_by(
                user_id=userID, id=bookableID).first()
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a bookable item ==> ID={}".format(bookableID), path=request.path
                                                   )
            session.query(Bookables).filter_by(
                user_id=userID, id=bookableID).delete()
            session.commit()

            return None, 204
        except (KeyError, ValueError):
            pass


class BookableCollection(Resource):
    def get(self, userID):
        try:
            #query the user based on the ID
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            bookables = session.query(Bookables).all()
            #getting a instance of our api which consists of resources' routes
            singelton = APIInitializer.getInstance()
            body = BookableBuilder(items=[])
            for i in bookables:
                item = MasonBuilder(name=i.name, details=i.details)
                item.add_control("self", singelton.get_api().url_for(
                    BookableCollection, userID=userID))
                item.add_control("profile", href="/profiles/Bookable/")
                body["items"].append(item)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", singelton.get_api().url_for(
                BookableCollection, userID=userID))
            body.add_control_user(url=singelton.get_api().url_for(
                UserItem, userID=userID))
            return Response(json.dumps(body), 200, mimetype=MASON)

        except (KeyError, ValueError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no attribute 'name' found in the request,'name'is string", path=request.path
                                               )

class BookableItem(Resource):
    pass

class SlotCollectionofUser(Resource):
    def get(self, userID, bookableID):
        try:
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            
            bookable_item = session.query(Bookables).filter_by(user_id=userID, id=bookableID).first()
            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such Bookable ==> ID={}".format(bookableID), path=request.path
                                                   )
            slots = session.query(Slot).filter_by(user_id=userID, bookable_id=bookableID)
            singelton = APIInitializer.getInstance()
            body = SlotBuilder(items=[])
            
            for i in slots:
                item = MasonBuilder(starting_time=i.starting_time, ending_time=i.ending_time, availability=i.availability)
                item.add_control("self", singelton.get_api().url_for(
                    SlotItemofUser, userID=userID, bookableID=bookableID, slotID=i.id))
                item.add_control("profile", href="/profiles/Slot/")
                body["items"].append(item)
            
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", singelton.get_api().url_for(
                SlotCollectionofUser, userID=userID, bookableID=bookableID))
            body.add_control_add_slot(userID=userID, bookableID=bookableID, url=singelton.get_api().url_for(
                SlotCollectionofUser, userID=userID))
            body.add_control_bookable(userID=userID, bookableID=bookableID, url=singelton.get_api().url_for(
                BookableItemofUser, userID=userID, bookableID=bookableID))
            return Response(json.dumps(body), 200, mimetype=MASON)

        except (KeyError, ValueError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no attribute 'name' found in the request,'name'is string", path=request.path
                                               )

    def post(self, userID, bookableID):
        if request.is_json:
            try:
                user = session.query(User).filter_by(id=userID).first()
                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                       message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                       )
                
                slot = [Slot(
                    starting_time=request.json['starting_time'], ending_time=request.json['ending_time'], availability=request.json['availability'], user_id=userID, bookable_id=bookableID)]
                session.add_all(slot)
                session.commit()
                return None, 201
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request, name is string", path=request.path
                                                   )

        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

class SlotItemofUser(Resource):
    def get(self, userID, bookableID, slotID):
        try:
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such user ==> ID={}".format(userID), path=request.path
                                                   )
            bookable_item = session.query(Bookables).filter_by(
                user_id=userID, id=bookableID).first()
            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such bookable item ==> ID={}".format(bookableID), path=request.path
                                                   )
                                                   
            slot_item = session.query(Slot).filter_by(
                user_id=userID, bookable_id=bookableID, slot_id=slotID).first()
            if slot_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such slot item ==> ID={}".format(bookableID), path=request.path
                                                   )
                                                   
            singelton = APIInitializer.getInstance()
            body = SlotBuilder(
                id=slotID, user_id=userID, bookable_id=bookableID, starting_time=i.starting_time, ending_time=i.ending_time, availability=i.availability)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", request.path)
            body.add_control("collection", singelton.get_api().url_for(
                    SlotCollectionofUser, userID=userID, bookableID=bookableID))
            body.add_control_user(
                singelton.get_api().url_for(UserCollection))
            body.add_control_edit(userID=userID, bookableID=bookableID, slotID=slotID,
                                  url=request.path)
            body.add_control_delete(
                userID=userID, bookableID=bookableID, slotID=slotID, url=request.path)
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            pass

    def put(self, userID, bookableID, slotID):
        if request.json:
            try:
                new_starting_time = request.json["starting_time"]
                new_ending_time = request.json["ending_time"]
                new_availability = request.json['availability']
                user = session.query(User).filter_by(id=userID).first()
                bookable_item = session.query(Bookables).filter_by(
                    user_id=userID, id=bookableID).first()
                slot_item = session.query(Slot).filter_by(user_id=userID, bookable_id=bookableID, slot_id=slotID).first()
                if new_starting_time is None or new_ending_time is None or new_availability is None:
                    raise ValueError()

                slot_item.starting_time = new_starting_time
                slot_item.ending_time = new_ending_time
                slot_item.availability = new_availability
                session.commit()
                return None, 204
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="mandatory fields could not be found in the request", path=request.path
                                                   )
            except (TypeError, exc.IntegrityError, exc.InvalidRequestError):
                return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                                   message="Requests must be JSON", path=request.path
                                                   )
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID, bookableID, slotID):
        try:
            slot_item = session.query(Slot).filter_by(
                user_id=userID, bookable_id=bookableID, slot_id=slotID).first()
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            if slot_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such slot item ==> ID={}".format(bookableID), path=request.path
                                                   )
            session.query(Slot).filter_by(
                user_id=userID, bookable_id=bookableID, slot_id=slotID).delete()
            session.commit()

            return None, 204
        except (KeyError, ValueError):
            pass
