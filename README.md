# PWP SPRING 2020
# PROJECT NAME
Booking Managment System
# Group information
* Student 1. Adnanul Islam; Email: aislam19@student.oulu.fi
* Student 2. Kursat Talha Berk Yamanoglu; Email: yamanogluberk@gmail.com 
* Student 3. Mohammad Hassan Sadeghein; Email: h.sadeghein96@gmail.com


## Installing API
In this project we have used SQLite3 for the backend and SQLAlchemy as object-relational mapper. So the first thing you are going to need if you want to run this project is installing the dependencies, although all of these dependencies have been already provided in setup.py file on the root.
So use the command 
* pip install -e 
And the application will be ready for testing and running.

Then you can should set the environment variables for flask.
You can use following commands for windows.(For mac/linux you should use "export" instead of "set")
* set FLASK_APP=sensorhub
* set FLASK_ENV=development

Now our api is ready for testing and running

## Running API

For the first time you should initialize the database using command 
* flask init-db

Now you can run the api with command
* flask run

## Testing

To test the database and api functionality you can use pytest. If you dont have pytest install it with
* pip install pytest

Then you can use the following command in the project folder to run all test cases.
* pytest 

To obtain a coverage report you should run this command
* pytest --cov-report term-missing --cov=app

## Client
To start the client part, open __start.bat__ file.

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


