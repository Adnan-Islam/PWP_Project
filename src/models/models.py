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
    #Relationships
    bookables = relationship("Bookables",cascade="all,delete", back_populates="user",passive_deletes=True)
    

class Bookables(Base):
    __tablename__ = 'bookable'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64), nullable=False)
    details = Column(String(128), nullable=True)
    #Relationships
    user = relationship("User", back_populates="bookables", single_parent=True)
    resource_links = relationship("ResourceLink",cascade="all,delete", back_populates="bookable", passive_deletes=True)
    slots = relationship("Slot", cascade="all,delete", back_populates="bookable", passive_deletes=True)


class ResourceLink(Base):
    __tablename__ = 'resource_link'

    id = Column(Integer, primary_key=True)
    bookable_id = Column(Integer, ForeignKey("bookable.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(128), nullable=False)
    #Relationships
    bookable = relationship("Bookables", single_parent=True, back_populates="resource_links")


class Slot(Base):
    __tablename__ = "slot"
    __table_args__ = (
        CheckConstraint('owner_id <> client_id', name='NoSameUsers'),
        CheckConstraint('ending_time > starting_time', name='NoSameDate'),
    )
    
    id = Column(Integer, primary_key=True)
    starting_time = Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    ending_time = Column(DateTime, nullable=False)
    availability = Column(Boolean, nullable=False, default=True)
    booakble_id = Column(Integer, ForeignKey("bookable.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    #Relationships
    bookable = relationship("Bookables", single_parent=True, back_populates="slots")
    owner = relationship("User", backref=backref("slot_owner", passive_deletes=True), foreign_keys=[owner_id])
    client = relationship("User", backref="slot_client", foreign_keys=[client_id])
    book_requests = relationship("BookRequest", cascade="all,delete", back_populates="slot", passive_deletes=True)


class BookRequest(Base):
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
