import datetime
import click
from sqlalchemy import CheckConstraint
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from flask.cli import with_appcontext
from bookingapi import db

# for creating foreign key relationship between the tables
from sqlalchemy.orm import relationship, backref


# Classes that are gonna be tables in SQLite

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    #Relationships
    bookables = relationship("Bookables",cascade="all,delete", back_populates="user",passive_deletes=True)
    

class Bookables(db.Model):
    __tablename__ = 'bookable'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64), nullable=False)
    details = Column(String(128), nullable=True)
    #Relationships
    user = relationship("User", back_populates="bookables", single_parent=True)
    resource_links = relationship("ResourceLink",cascade="all,delete", back_populates="bookable", passive_deletes=True)
    slots = relationship("Slot", cascade="all,delete", back_populates="bookable", passive_deletes=True)


class ResourceLink(db.Model):
    __tablename__ = 'resource_link'

    id = Column(Integer, primary_key=True)
    bookable_id = Column(Integer, ForeignKey("bookable.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(128), nullable=False)
    #Relationships
    bookable = relationship("Bookables", single_parent=True, back_populates="resource_links")


class Slot(db.Model):
    __tablename__ = "slot"
    __table_args__ = (
        CheckConstraint('owner_id <> client_id', name='NoSameUsers'),
        CheckConstraint('ending_time > starting_time', name='NoSameDate'),
    )
    
    id = Column(Integer, primary_key=True)
    starting_time = Column(String(64), nullable=False,
                           default=str(datetime.datetime.utcnow))
    ending_time = Column(String(64), nullable=False)
    availability = Column(Boolean, nullable=False, default=True)
    bookable_id = Column(Integer, ForeignKey("bookable.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    #Relationships
    bookable = relationship("Bookables", single_parent=True, back_populates="slots")
    owner = relationship("User", backref=backref("slot_owner", passive_deletes=True), foreign_keys=[owner_id])
    client = relationship("User", backref="slot_client", foreign_keys=[client_id])
    book_requests = relationship("BookRequest", cascade="all,delete", back_populates="slot", passive_deletes=True)


class BookRequest(db.Model):
    __tablename__ = "book_request"
    __table_args__ = (
        CheckConstraint('sender_id <> receiver_id', name='NoSameUsers'),
    )
    
    id = Column(Integer, primary_key=True)
    approved = Column(Boolean, nullable=True)
    slot_id = Column(Integer, ForeignKey("slot.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    #Relationships
    sender = relationship(
        "User", backref=backref("book_request_sender", passive_deletes=True), foreign_keys=[sender_id])
    receiver = relationship(
        "User", backref=backref("book_request_receiver", passive_deletes=True), foreign_keys=[receiver_id])
    slot = relationship("Slot", back_populates="book_requests")

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    

@click.command("gen-test-user")
@with_appcontext
def generate_test_data():
    s = User(
        name="testuser"
    )
    
    db.session.add(s)
    db.session.commit()