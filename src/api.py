from flask import Blueprint
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request

class APIInitializer:
    __instance = None
    api = None
    app = None
    @staticmethod
    def getInstance():
        """ Static access method. """
        if APIInitializer.__instance == None:
            APIInitializer()
        return APIInitializer.__instance

    @staticmethod
    def setApp(app):
        APIInitializer.app = app

    def __init__(self):
        APIInitializer.api = Api(APIInitializer.app)
        """ Virtually private constructor. """
        if APIInitializer.__instance != None:
            raise Exception("This class is a Singelton!")
        else:
            APIInitializer.__instance = self

    def get_api(self):
        return self.api
