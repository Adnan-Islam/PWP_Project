from models.models import User, Base
from api import Singleton
from utils import MasonBuilder, Utils, UserItemBuilder, LINK_RELATIONS_URL, MASON
from flask_restful import Resource
from flask import Flask, request,  abort, Response
from sqlalchemy import create_engine
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


engine = create_engine('sqlite:///books-collection.db')
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


class UserCollection(Resource):
    def post(self):
        print("POST ==> UserCollection")
        if request.is_json:
            if request.json is not None:
                try:
                    new_user = [User(name=request.json['name'])]
                    session.add_all(new_user)
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
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class UserItem(Resource):
    def get(self, userID):
        print("UserItem ==> Get")
        try:
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="Ther is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            singelton = Singleton.getInstance()
            body = UserItemBuilder(id=user.id, name=user.name)
            body.add_namespace("bookingmeta", LINK_RELATIONS_URL)
            body.add_control("self", request.path)
            body.add_control_add_user(singelton.api.url_for(UserCollection))
            body.add_control_edit_user(
                userID, singelton.get_api().url_for(UserItem, userID = userID))
            body.add_control_delete_user(
                userID, singelton.get_api().url_for(UserItem, userID = userID))
            # body.add_control_get_all_bookables(userId,api.url_for))
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            pass

    def edit(self, User):
        pass

    def delete(self, User):
        pass