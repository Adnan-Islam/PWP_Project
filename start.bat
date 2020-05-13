pip install -e .
set FLASK_APP=bookingapi
set FLASK_ENV=development
start ./client/static/html/log-in.html
if not exist ./instance/development.db (
	flask init-db
)
flask run

PAUSE