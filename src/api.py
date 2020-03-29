from flask import Blueprint
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
# from resources.users import UserCollection, UserItem

# api.add_resource(UserCollection, "/users")
# api.add_resource(UserItem, "/users/<userID>")


# @api_bp.route("/")
# def index():
#     return ""
# Initializing
# app = Flask(__name__)
# api = Api(app)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)

# if __name__ == '__main__':
#     app.run(debug=True)

class Singleton:
    __instance = None
    api = None
    app = None
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Singleton.__instance == None:
            Singleton()
        return Singleton.__instance

    @staticmethod
    def setApp(app):
        Singleton.app = app

    def __init__(self):
        # api_bp = Blueprint("api", __name__, url_prefix="/api")
        Singleton.api = Api(Singleton.app)
        """ Virtually private constructor. """
        if Singleton.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Singleton.__instance = self

    def get_api(self):
        return self.api
