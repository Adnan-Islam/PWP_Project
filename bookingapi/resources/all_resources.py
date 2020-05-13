import json
import os
import sys
import inspect
from flask_restful import Api, Resource
from flask import Flask, request,  abort, Response, url_for
from sqlalchemy import create_engine, update, delete
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
from bookingapi.models import User, Bookables, Slot
from bookingapi.utils import MasonBuilder, Utils, UserItemBuilder, BookableBuilder, SlotBuilder, LINK_RELATIONS_URL, MASON
from bookingapi import db


class UserCollection(Resource):

    """
    Create a user with name and ID
    """

    def post(self):

        try:
            # Check to find out the request is in the right format
            request_json = json.loads(request.data)
            # Creating new user
            new_user = User(name=request_json['name'])

        # The request JSON is not we expected for
        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
        # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )
            # Commiting into database
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)

            returningvalue = {}
            returningvalue['id'] = new_user.id

            # if there is no error then return 201
            return Response(json.dumps(returningvalue), 201, headers={"location": url_for("api.useritem", user_id=new_user.id)})


class UserItem(Resource):


    """ Get a single user based on its id"""

    def get(self, user_id):

        # Query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()

        # If there is no such a user 404 will be returned
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        # building the controler for our response
        body = UserItemBuilder(id=user.id, name=user.name)

        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", request.path)

        body.add_control_add_user(url_for("api.usercollection"))

        body.add_control_edit_user(
            user_id, url_for("api.useritem", user_id=user_id))

        body.add_control_delete_user(
            user_id, url_for("api.useritem", user_id=user_id))

        body.add_control_get_bookables_by(user_id=user_id, url=url_for(
            "api.booakblecollectionofuser", user_id=user_id))

        body.add_control_get_all_bookables(
            user_id=user_id, url=url_for("api.bookablecollection", user_id=user_id))

        # User has been found without any problem
        return Response(json.dumps(body), 200, mimetype=MASON)



    """Update a user with new information"""

    def put(self, user_id):
        try:
            # Check to find out the request is in the right format
            request_json = json.loads(request.data)
            # New data which must  be replaced
            new_name = request_json["name"]
            if new_name is None:
                raise ValueError()

        # The request JSON is not we expected for
        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
        # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()

        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        # updating user's information
        user.name = new_name
        db.session.commit()
        return None, 204



    """Delete a user based on its ID"""

    def delete(self, user_id):
        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )
        db.session.query(User).filter_by(id=user_id).delete()
        db.session.commit()

        return None, 204


class BooakbleCollectionofUser(Resource):


    """ Get a collection of user's bookables"""

    def get(self, user_id):

        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )
        bookables = db.session.query(Bookables).filter_by(user_id=user_id)

        body = BookableBuilder(items=[])
        for i in bookables:
            item = MasonBuilder(id=i.id, name=i.name, details=i.details)
            
            item.add_control("self", url_for(
                "api.booakblecollectionofuser", user_id=user_id))

            body["items"].append(item)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", url_for(
            "api.booakblecollectionofuser", user_id=user_id))

        body.add_control_add_bookable(user_id=user_id, url=url_for(
            "api.booakblecollectionofuser", user_id=user_id))

        body.add_control_user(url=url_for("api.useritem", user_id=user_id))

        
        return Response(json.dumps(body), 200, mimetype=MASON)



    """Create a bookable for a user"""

    def post(self, user_id):
        try:
            # Check to find out the request is in the right format
            request_json = json.loads(request.data)
            # The request JSON is not we expected for

            user = db.session.query(User).filter_by(id=user_id).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                                   )
            new_bookable = Bookables(
                name=request.json['name'], details=request.json['details'], user_id=user_id)
            db.session.add(new_bookable)
            db.session.commit()
            db.session.refresh(new_bookable)

            return Response(None, 201, headers={"location": url_for("api.bookableitemofuser", user_id=user_id, bookable_id=new_bookable.id)})

        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
            # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class BookableItemofUser(Resource):


    """Get a bookable of a user based on its ID"""

    def get(self, user_id, bookable_id):
        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )
        # query the bookable based on the user and its ID
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a bookable item ==> ID={}".format(bookable_id), path=request.path
                                               )
        #Create a controller
        body = BookableBuilder(
            id=bookable_id, user_id=user_id, name=bookable_item.name, details=bookable_item.details)

        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", request.path)

        body.add_control("collection", url_for(
            "api.booakblecollectionofuser", user_id=user_id))

        body.add_control_user(url=url_for("api.useritem", user_id=user_id))

        body.add_control_slots_of(user_id=user_id, bookable_id=bookable_id,
                                  url=url_for("api.slotcollectionofuser", user_id=user_id, bookable_id=bookable_id))

        body.add_control_edit(user_id=user_id, bookable_id=bookable_id,
                              url=request.path)
                              
        body.add_control_delete(
            user_id=user_id, bookable_id=bookable_id, url=request.path)


        return Response(json.dumps(body), 200, mimetype=MASON)



    """Update a bookable of a user based on its ID"""

    def put(self, user_id, bookable_id):
        try:
            # Check to find out the request is in the right format
            request_json = json.loads(request.data)
            new_name = request_json["name"]
            new_details = request_json['details']
            if new_name is None or new_details is None:
                raise ValueError()
        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
            # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        if user is None or bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        bookable_item.name = new_name
        bookable_item.details = new_details
        db.session.commit()
        return None, 204



    """Delete a bookable of a user based on its ID"""

    def delete(self, user_id, bookable_id):
        #Query the bookable and the user
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None or bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).delete()
        db.session.commit()

        return None, 204


class BookableCollection(Resource):


    """Get all bookables existing in our database"""

    def get(self, user_id):

        # query the user based on the ID
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        bookables = db.session.query(Bookables).all()
        

        #Create a Controller
        body = BookableBuilder(items=[])
        for i in bookables:
            item = MasonBuilder(name=i.name, details=i.details)

            item.add_control("self", url_for(
                "api.bookablecollection", user_id=user_id))

            body["items"].append(item)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", url_for(
            "api.bookablecollection", user_id=user_id))

        body.add_control_user(url=url_for("api.useritem", user_id=user_id))


        return Response(json.dumps(body), 200, mimetype=MASON)


class BookableItem(Resource):
    pass


class SlotCollectionofUser(Resource):


    """ Get a collection of slots of a bookable"""

    def get(self, user_id, bookable_id):
        # query the user based on the ID

        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such Bookable ==> ID={}".format(bookable_id), path=request.path
                                               )
        slots = db.session.query(Slot).filter_by(
            owner_id=user_id, bookable_id=bookable_id)

        #Create a Controller
        body = SlotBuilder(items=[])

        for i in slots:
            item = MasonBuilder(id=i.id, starting_time=i.starting_time,
                                ending_time=i.ending_time, availability=i.availability)
            item.add_control("self", url_for(
                "api.slotitemofuser", user_id=user_id, bookable_id=bookable_id, slot_id=i.id))
            body["items"].append(item)

        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", url_for(
            "api.slotcollectionofuser", user_id=user_id, bookable_id=bookable_id))

        body.add_control_add_slot(user_id=user_id, bookable_id=bookable_id, url=url_for(
            "api.slotcollectionofuser", user_id=user_id, bookable_id=bookable_id))

        body.add_control_bookable(user_id=user_id, bookable_id=bookable_id, url=url_for(
            "api.bookableitemofuser", user_id=user_id, bookable_id=bookable_id))
        return Response(json.dumps(body), 200, mimetype=MASON)



    """Create a slot for a bookable"""

    def post(self, user_id, bookable_id):
        try:
            #Check the request is in the right format
            request_json = json.loads(request.data)
            # query the user based on the ID
            user = db.session.query(User).filter_by(id=user_id).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such user ==> ID={}".format(user_id), path=request.path
                                                   )

            bookable_item = db.session.query(Bookables).filter_by(
                user_id=user_id, id=bookable_id).first()
            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such bookable item ==> ID={}".format(bookable_id), path=request.path
                                                   )

            slot = Slot(
                starting_time=request_json['starting_time'], ending_time=request_json['ending_time'], availability=request_json['availability'], owner_id=user_id, bookable_id=bookable_id)

        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
            # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )
        db.session.add(slot)
        db.session.commit()
        db.session.refresh(slot)
        return Response(None, 201, headers={"location": url_for("api.slotitemofuser", user_id=user_id, bookable_id=bookable_id, slot_id=slot.id)})


class SlotItemofUser(Resource):


    """Get a slot of a bookable item"""

    def get(self, user_id, bookable_id, slot_id):

        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such user ==> ID={}".format(user_id), path=request.path
                                               )
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such bookable item ==> ID={}".format(bookable_id), path=request.path
                                               )

        slot_item = db.session.query(Slot).filter_by(
            owner_id=user_id, bookable_id=bookable_id, id=slot_id).first()
        if slot_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such slot item ==> ID={}".format(bookable_id), path=request.path
                                               )
        #create a coontroller
        body = SlotBuilder(
            id=slot_id, user_id=user_id, bookable_id=bookable_id, starting_time=slot_item.starting_time,
            ending_time=slot_item.ending_time, availability=slot_item.availability)

        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)

        body.add_control("self", request.path)

        body.add_control("collection", url_for(
            "api.slotcollectionofuser", user_id=user_id, bookable_id=bookable_id))

        body.add_control_user(url_for("api.usercollection"))

        body.add_control_edit(user_id=user_id, bookable_id=bookable_id, slot_id=slot_id,
                              url=request.path)

        body.add_control_delete(
            user_id=user_id, bookable_id=bookable_id, slot_id=slot_id, url=request.path)

        return Response(json.dumps(body), 200, mimetype=MASON)



    """Update a slot of a bookalbe"""

    def put(self, user_id, bookable_id, slot_id):
        try:
            new_starting_time = request.json["starting_time"]
            new_ending_time = request.json["ending_time"]
            new_availability = request.json['availability']

            # query the user based on the ID
            user = db.session.query(User).filter_by(id=user_id).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such user ==> ID={}".format(user_id), path=request.path
                                                   )

            bookable_item = db.session.query(Bookables).filter_by(
                user_id=user_id, id=bookable_id).first()

            if bookable_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such bookable item ==> ID={}".format(bookable_id), path=request.path
                                                   )

            slot_item = db.session.query(Slot).filter_by(
                owner_id=user_id, bookable_id=bookable_id, id=slot_id).first()

            if slot_item is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such slot item ==> ID={}".format(bookable_id), path=request.path
                                                   )

            if new_starting_time is None or new_ending_time is None or new_availability is None:
                raise ValueError()
        except (IndexError, KeyError, TypeError):
            return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                               message="no proper attributes", path=request.path
                                               )
            # The request JSON is not a JSON
        except (ValueError):
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )
        slot_item.starting_time = new_starting_time
        slot_item.ending_time = new_ending_time
        slot_item.availability = new_availability

        db.session.commit()
        return None, 204



    """Delete a slot of a bookalbe"""

    def delete(self, user_id, bookable_id, slot_id):

        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(user_id), path=request.path
                                               )

        bookable_item = db.session.query(Bookables).filter_by(
            user_id=user_id, id=bookable_id).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such bookable item ==> ID={}".format(bookable_id), path=request.path
                                               )

        slot_item = db.session.query(Slot).filter_by(
            owner_id=user_id, bookable_id=bookable_id, id=slot_id).first()
        if slot_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such slot item ==> ID={}".format(bookable_id), path=request.path
                                               )
        db.session.query(Slot).filter_by(
            owner_id=user_id, bookable_id=bookable_id, id=slot_id).delete()
        db.session.commit()

        return None, 204
