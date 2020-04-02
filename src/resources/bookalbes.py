from models.models import User, Base, Bookables
from api import APIInitializer
from utils import MasonBuilder, Utils, UserItemBuilder, BookableBuilder, LINK_RELATIONS_URL, MASON
from resources.users import UserItem
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


engine = create_engine('sqlite:///books-collection.db',
                       connect_args={'check_same_thread': True})
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


class BooakbleCollectionofUser(Resource):
    def get(self, userID):
        try:
            user = session.query(User).filter_by(id=userID).first()
            if user is None:
                return Utils.create_error_response(status_code=404, title="Not Found",
                                                   message="There is no such a user ==> ID={}".format(userID), path=request.path
                                                   )
            bookables = session.query(Bookables).filter_by(user_id=userID)
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
            if request.json is not None:
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
        else:
            return Utils.create_error_response(status_code=415, title="Unsupported media type",
                                               message="Requests must be JSON", path=request.path
                                               )


class BookableItemofUser(Resource):
    pass


class BookableCollection(Resource):
    pass


class BookableItem(Resource):
    pass
