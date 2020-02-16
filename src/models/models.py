import datetime

from sqlalchemy import CheckConstraint


from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean

# for configuration and class code
from sqlalchemy.ext.declarative import declarative_base

# for creating foreign key relationship between the tables
from sqlalchemy.orm import relationship, backref

# for configuration
from sqlalchemy import create_engine

Base = declarative_base()

# Classes that are gonna be tables in SQLite


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    bookable = relationship("Bookables", back_populates="user")


class Bookables(Base):
    __tablename__ = 'bookable'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String(64), nullable=False)
    details = Column(String(128), nullable=True)
    user = relationship(
        "User", cascade="all, delete-orphan", single_parent=True)
    resource_link = relationship("ResourceLink", back_populates="bookable")
    slot = relationship("Slot", back_populates="bookable")


class ResourceLink(Base):
    __tablename__ = 'resource_link'

    id = Column(Integer, primary_key=True)
    bookable_id = Column(Integer, ForeignKey("bookable.id"))
    url = Column(String(128), nullable=False)
    bookable = relationship(
        "Bookables", cascade="all, delete-orphan", single_parent=True, back_populates="resource_link")


class Slot(Base):
    __tablename__ = "slot"
    __table_args__ = (
        CheckConstraint('owner_id <> client_id', name='NoSameUsers'),
    )
    id = Column(Integer, primary_key=True)
    starting_time = Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    ending_time = Column(DateTime, nullable=False)
    availability = Column(Boolean, nullable=False, default=True)
    booakble_id = Column(Integer, ForeignKey("bookable.id"))
    owner_id = Column(Integer, ForeignKey("user.id"))
    client_id = Column(Integer, ForeignKey("user.id"))
    bookable = relationship(
        "Bookables", cascade="all, delete-orphan", single_parent=True, back_populates="slot")
    owner = relationship(
        "User", backref="slot_owner", foreign_keys=[owner_id])
    client = relationship(
        "User", backref="slot_client", foreign_keys=[client_id])
    book_request = relationship(
        "BookRequest", back_populates="slot")


class BookRequest(Base):
    __tablename__ = "book_request"
    __table_args__ = (
        CheckConstraint('sender_id <> receiver_id', name='NoSameUsers'),
    )
    id = Column(Integer, primary_key=True)
    approved = Column(Boolean, nullable=True)
    slot_id = Column(Integer, ForeignKey("slot.id"))
    sender_id = Column(Integer, ForeignKey("user.id"))
    receiver_id = Column(Integer, ForeignKey("user.id"))

    sender = relationship(
        "User", backref="book_request_sender", foreign_keys=[sender_id])
    receiver = relationship(
        "User", backref="book_request_reveicer", foreign_keys=[receiver_id])
    slot = relationship("Slot", back_populates="book_request")
