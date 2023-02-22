from datetime import datetime
from flask_login import UserMixin
import os

from . import db


def setup_db(app):
    database_path = os.getenv("DATABASE_URL")

    if database_path is None:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///testdb.sqlite"
        print("Using test database")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_path.replace("://", "ql://", 1)
        print("Using DATABASE_URL")

    print(app.config["SQLALCHEMY_DATABASE_URI"])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    venue_name = db.Column(db.String(255))
    venue_address = db.Column(db.String(255))
    status = db.Column(db.String(255))
    desc = db.Column(db.Text)
    tickets = db.Column(db.Integer)
    price = db.Column(db.Float)
    image_data = db.Column(db.LargeBinary)
    image_render = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    comments = db.relationship("Comment", backref="event")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    desc = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    username = db.Column(db.String(255), index=True, nullable=False)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    tickets = db.Column(db.Integer)
    price = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), index=True, nullable=False, unique=True)
    hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)

    events = db.relationship("Event", backref="user")
    comments = db.relationship("Comment", backref="user")
    bookings = db.relationship("Booking", backref="user")
