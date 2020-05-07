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
    def post(self):

        # Check if the request is in the right form
        if request.is_json:
            try:

                # Creating new user
                new_user = User(name=request.json['name'])

                # add changes to the database
                db.session.add(new_user)

                # commiting the changes
                db.session.commit()

                #returning the id of the created user
                db.session.refresh(new_user)
                
                returningvalue = {}
                returningvalue['id'] = new_user.id
                # if there is no error then return 201
                return Response(json.dumps(returningvalue), 201, headers={"location":url_for("api.useritem", userID=new_user.id)})

           
            # The request JSON is not we expected for
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request,'name'is string", path=request.path
                                                   )
        # The request JSON is not a JSON
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class UserItem(Resource):
    def get(self, userID):
        
        # Query the user based on the ID
        user = db.session.query(User).filter_by(id=userID).first()

        # If there is no such a user 404 will be returned
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )

        # building the controler for our response
        body = UserItemBuilder(id=user.id, name=user.name)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", request.path)
        body.add_control_add_user(url_for("api.usercollection"))
        body.add_control_edit_user(userID, url_for("api.useritem", userID=userID))
        body.add_control_delete_user(userID, url_for("api.useritem", userID=userID))
        body.add_control_get_bookables_by(userID=userID, url=url_for("api.booakblecollectionofuser", userID=userID))
        body.add_control_get_all_bookables(userID=userID, url=url_for("api.bookablecollection", userID=userID))

        # User has been found without any problem
        return Response(json.dumps(body), 200, mimetype=MASON)
        

    def put(self, userID):
        # Check if the request is in the right form
        if request.is_json :
            try:
                # New data which must  be replaced
                new_name = request.json["name"]

                # query the user based on the ID
                user = db.session.query(User).filter_by(id=userID).first()

                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
                if new_name is None:
                    raise ValueError()

                # updating user's information
                user.name = new_name
                db.session.commit()
                return None, 204
            # The request JSON is not we expected for
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' found in the request,'name'is string", path=request.path
                                                   )
            
        # Unsupported media type like the request JSON is malformed
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID):
        
        # query the user based on the ID
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
        db.session.query(User).filter_by(id=userID).delete()
        db.session.commit()

        return None, 204
        


class BooakbleCollectionofUser(Resource):
    def get(self, userID):
        
        # query the user based on the ID
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
        bookables = db.session.query(Bookables).filter_by(user_id=userID)

        body = BookableBuilder(items=[])
        for i in bookables:
            item = MasonBuilder(id = i.id, name=i.name, details=i.details)
            item.add_control("self", url_for("api.booakblecollectionofuser", userID=userID))
            body["items"].append(item)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.booakblecollectionofuser", userID=userID))
        body.add_control_add_bookable(userID=userID, url=url_for("api.booakblecollectionofuser", userID=userID))
        body.add_control_user(url=url_for("api.useritem", userID=userID))
        return Response(json.dumps(body), 200, mimetype=MASON)

     
    def post(self, userID):
        if request.is_json:
            try:
                user = db.session.query(User).filter_by(id=userID).first()
                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                       message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                       )
                new_bookable = Bookables(
                    name=request.json['name'], details=request.json['details'], user_id=userID)
                db.session.add(new_bookable)
                db.session.commit()
                db.session.refresh(new_bookable)
                
                
                return Response(None, 201, headers={"location":url_for("api.bookableitemofuser", userID=userID, bookableID=new_bookable.id)})
            
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
        
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=userID, id=bookableID).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a bookable item ==> ID={}".format(bookableID), path=request.path
                                               )

        body = BookableBuilder(
            id=bookableID, user_id=userID, name=bookable_item.name, details=bookable_item.details)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", request.path)
        body.add_control("collection", url_for("api.booakblecollectionofuser", userID=userID))
        body.add_control_user(url=url_for("api.useritem", userID=userID))
        body.add_control_slots_of(userID=userID, bookableID=bookableID,
                                  url=url_for("api.slotcollectionofuser", userID=userID, bookableID=bookableID))
        body.add_control_edit(userID=userID, bookableID=bookableID,
                              url=request.path)
        body.add_control_delete(
            userID=userID, bookableID=bookableID, url=request.path)
        return Response(json.dumps(body), 200, mimetype=MASON)
        

    def put(self, userID, bookableID):
        if request.is_json:
            try:
                new_name = request.json["name"]
                new_details = request.json['details']
                user = db.session.query(User).filter_by(id=userID).first()
                bookable_item = db.session.query(Bookables).filter_by(
                    user_id=userID, id=bookableID).first()
                if user is None or bookable_item is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
                if new_name is None or new_details is None:
                    raise ValueError()

                bookable_item.name = new_name
                bookable_item.details = new_details
                db.session.commit()
                return None, 204
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="no attribute 'name' or 'details' found in the request,'name' and 'details' are string", path=request.path
                                                   )
           
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID, bookableID):
        
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=userID, id=bookableID).first()
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None or bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
        
        db.session.query(Bookables).filter_by(
            user_id=userID, id=bookableID).delete()
        db.session.commit()

        return None, 204
        


class BookableCollection(Resource):
    def get(self, userID):
        
        # query the user based on the ID
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
                                               
        bookables = db.session.query(Bookables).all()

        body = BookableBuilder(items=[])
        for i in bookables:
            item = MasonBuilder(name=i.name, details=i.details)
            item.add_control("self", url_for("api.bookablecollection", userID=userID))
            body["items"].append(item)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.bookablecollection", userID=userID))
        body.add_control_user(url=url_for("api.useritem", userID=userID))
        return Response(json.dumps(body), 200, mimetype=MASON)

        


class BookableItem(Resource):
    pass


class SlotCollectionofUser(Resource):
    def get(self, userID, bookableID):
        
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )

        bookable_item = db.session.query(Bookables).filter_by(
            user_id=userID, id=bookableID).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such Bookable ==> ID={}".format(bookableID), path=request.path
                                               )
        slots = db.session.query(Slot).filter_by(
            owner_id=userID, bookable_id=bookableID)

        body = SlotBuilder(items=[])

        for i in slots:
            item = MasonBuilder(starting_time=i.starting_time,
                                ending_time=i.ending_time, availability=i.availability)
            item.add_control("self", url_for("api.slotitemofuser", userID=userID, bookableID=bookableID, slotID=i.id))
            body["items"].append(item)

        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.slotcollectionofuser", userID=userID, bookableID=bookableID))
        body.add_control_add_slot(userID=userID, bookableID=bookableID, url=url_for("api.slotcollectionofuser", userID=userID, bookableID=bookableID))
        body.add_control_bookable(userID=userID, bookableID=bookableID, url=url_for("api.bookableitemofuser", userID=userID, bookableID=bookableID))
        return Response(json.dumps(body), 200, mimetype=MASON)

       

    def post(self, userID, bookableID):
        if request.is_json:
            try:
                user = db.session.query(User).filter_by(id=userID).first()
                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such user ==> ID={}".format(userID), path=request.path
                                                   )
                
                bookable_item = db.session.query(Bookables).filter_by(
                    user_id=userID, id=bookableID).first()
                if bookable_item is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such bookable item ==> ID={}".format(bookableID), path=request.path
                                                   )
                                                   
                slot = Slot(
                    starting_time=request.json['starting_time'], ending_time=request.json['ending_time'], availability=request.json['availability'], owner_id=userID, bookable_id=bookableID)
                db.session.add(slot)
                db.session.commit()
                db.session.refresh(slot)
                return Response(None, 201, headers={"location":url_for("api.slotitemofuser", userID=userID, bookableID=bookableID, slotID=slot.id)})
            
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="attribute missing in the request, look for schema", path=request.path
                                                   )

        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class SlotItemofUser(Resource):
    def get(self, userID, bookableID, slotID):
        
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such user ==> ID={}".format(userID), path=request.path
                                               )
        bookable_item = db.session.query(Bookables).filter_by(
            user_id=userID, id=bookableID).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such bookable item ==> ID={}".format(bookableID), path=request.path
                                               )

        slot_item = db.session.query(Slot).filter_by(
            owner_id=userID, bookable_id=bookableID, id=slotID).first()
        if slot_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such slot item ==> ID={}".format(bookableID), path=request.path
                                               )


        body = SlotBuilder(
            id=slotID, user_id=userID, bookable_id=bookableID, starting_time=slot_item.starting_time,
            ending_time=slot_item.ending_time, availability=slot_item.availability)
        body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
        body.add_control("self", request.path)
        body.add_control("collection", url_for("api.slotcollectionofuser", userID=userID, bookableID=bookableID))
        body.add_control_user(url_for("api.usercollection"))
        body.add_control_edit(userID=userID, bookableID=bookableID, slotID=slotID,
                              url=request.path)
        body.add_control_delete(
            userID=userID, bookableID=bookableID, slotID=slotID, url=request.path)
        return Response(json.dumps(body), 200, mimetype=MASON)
        

    def put(self, userID, bookableID, slotID):
        if request.is_json:
            try:
                new_starting_time = request.json["starting_time"]
                new_ending_time = request.json["ending_time"]
                new_availability = request.json['availability']
                
                user = db.session.query(User).filter_by(id=userID).first()
                if user is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such user ==> ID={}".format(userID), path=request.path
                                                   )
                
                bookable_item = db.session.query(Bookables).filter_by(
                    user_id=userID, id=bookableID).first()
                if bookable_item is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such bookable item ==> ID={}".format(bookableID), path=request.path
                                                   )
                
                slot_item = db.session.query(Slot).filter_by(
                    owner_id=userID, bookable_id=bookableID, id=slotID).first()
                
                if slot_item is None:
                    return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such slot item ==> ID={}".format(bookableID), path=request.path
                                                   )
                
                if new_starting_time is None or new_ending_time is None or new_availability is None:
                    raise ValueError()

                slot_item.starting_time = new_starting_time
                slot_item.ending_time = new_ending_time
                slot_item.availability = new_availability
                db.session.commit()
                return None, 204
            except (KeyError, ValueError):
                return Utils.create_error_response(status_code=400, title="Invalid JSON document",
                                                   message="mandatory fields could not be found in the request", path=request.path
                                                   )
            
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )

    def delete(self, userID, bookableID, slotID):
                    
        user = db.session.query(User).filter_by(id=userID).first()
        if user is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such a user ==> ID={}".format(userID), path=request.path
                                               )
                                               
        bookable_item = db.session.query(Bookables).filter_by(
                user_id=userID, id=bookableID).first()
        if bookable_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such bookable item ==> ID={}".format(bookableID), path=request.path
                                               ) 
                                               
        slot_item = db.session.query(Slot).filter_by(
                owner_id=userID, bookable_id=bookableID, id=slotID).first()
        if slot_item is None:
            return Utils.create_error_response(status_code=404, title="Not Found",
                                               message="There is no such slot item ==> ID={}".format(bookableID), path=request.path
                                               )
        db.session.query(Slot).filter_by(
            owner_id=userID, bookable_id=bookableID, id=slotID).delete()
        db.session.commit()

        return None, 204
        
