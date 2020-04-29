import datetime
from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean, CheckConstraint
# Resources
from resources.users import UserCollection, UserItem, BooakbleCollectionofUser, BookableItemofUser, BookableCollection, SlotCollectionofUser, SlotItemofUser

from api import APIInitializer
# for creating foreign key relationship between the tables
from sqlalchemy.orm import relationship, backref

# Initializing
app = Flask(__name__)
CORS(app)
APIInitializer.setApp(app)
singelton = APIInitializer.getInstance()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Resource routing
singelton.get_api().add_resource(UserCollection, "/api/users/")
singelton.get_api().add_resource(UserItem, "/api/users/<userID>/")
singelton.get_api().add_resource(BookableCollection,
                                 "/api/users/<userID>/bookables/")                               
singelton.get_api().add_resource(BooakbleCollectionofUser,
                                 "/api/users/<userID>/my_bookables/")
singelton.get_api().add_resource(BookableItemofUser,
                                 "/api/users/<userID>/my_bookables/<bookableID>/")
singelton.get_api().add_resource(SlotCollectionofUser,
                                 "/api/users/<userID>/my_bookables/<bookableID>/slots/")
singelton.get_api().add_resource(SlotItemofUser,
                                 "/api/users/<userID>/my_bookables/<bookableID>/slots/<slotID>/")

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)
