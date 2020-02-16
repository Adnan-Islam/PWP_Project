# PWP SPRING 2020
# PROJECT NAME
Booking Managment System
# Group information
* Student 1. Adnanul Islam; Email: aislam19@student.oulu.fi
* Student 2. Kursat Talha Berk Yamanoglu; Email: yamanogluberk@gmail.com 
* Student 3. Mohammad Hassan Sadeghein; Email: h.sadeghein96@gmail.com


## Creating Database
In this project we have used SQLite3 for the backend and SQLAlchemy as object-relational mapper. So the first thing you are going to need if you want to run this project is installing the dependencies, although all of these dependencies have been already provided in requirements.txt file on the root.
You can use either 
* pip install -r requirements.txt<br/>
 or
* pip install Flask
* pip install pysqlite3
* pip install flask-sqlalchemy

Then you can run the database_setup.py to initialize the database and Populate.py to populate the database with some dummy data.
You can use following commands
* python database_setup.py
* python Populate.py

To test the database implementation you can use pytest and project_db_test.py file. If you dont have pytest install it with
* pip install pytest
then you can use the following command in the project folder to run all test cases.
* pytest 


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


