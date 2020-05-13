from flask import Blueprint
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS

# Resources
from bookingapi.resources.all_resources import UserCollection, UserItem, BooakbleCollectionofUser, BookableItemofUser, BookableCollection, SlotCollectionofUser, SlotItemofUser

api_bp = Blueprint("api", __name__)
cors = CORS(api_bp, resources={r"/api/*": {"origins": "*"}})
api = Api(api_bp)


# Resource routing
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<userID>/")
api.add_resource(BookableCollection, "/api/users/<userID>/bookables/")
api.add_resource(BooakbleCollectionofUser, "/api/users/<userID>/my_bookables/")
api.add_resource(BookableItemofUser,
                 "/api/users/<userID>/my_bookables/<bookableID>/")
api.add_resource(SlotCollectionofUser,
                 "/api/users/<userID>/my_bookables/<bookableID>/slots/")
api.add_resource(
    SlotItemofUser, "/api/users/<userID>/my_bookables/<bookableID>/slots/<slotID>/")


@api_bp.route("/")
def index():
    return ""
