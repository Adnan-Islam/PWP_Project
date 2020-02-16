from sqlalchemy.engine import Engine
from sqlalchemy import event
# for configuration
from sqlalchemy import create_engine

# our models
from models.models import Base


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# creates a create_engine instance at the bottom of the file
engine = create_engine('sqlite:///books-collection.db', echo=True)

Base.metadata.create_all(engine)
