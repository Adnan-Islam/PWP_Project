
# for configuration
from sqlalchemy import create_engine

# our models
from models.models import Base
# creates a create_engine instance at the bottom of the file
engine = create_engine('sqlite:///books-collection.db', echo=True)

Base.metadata.create_all(engine)
