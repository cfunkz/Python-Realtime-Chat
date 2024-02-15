from . import db
from flask_login import UserMixin
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Define the association table for users and rooms
user_room_association = db.Table('user_rooms',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id')),
    db.Column('room_id', db.String(36), db.ForeignKey('room.id'))
)
admin_rooms_association = db.Table('admin_rooms',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id')),
    db.Column('room_id', db.String(36), db.ForeignKey('room.id'))
)

class Room(db.Model):
    id = db.Column(db.String(36), default=generate_uuid, primary_key=True)
    room_name = db.Column(db.String(50)) # Room name
    is_private = db.Column(db.Boolean, default=False) # Private room
    admin_id = db.Column(db.String(36), db.ForeignKey('user.id')) # Admin id of the room
    invite_code = db.Column(db.String(6), default=False)
    description = db.Column(db.String(100))
    admin = db.relationship('User', foreign_keys=[admin_id])
    admins = db.relationship('User', secondary=admin_rooms_association, back_populates='admin_rooms')
    users = db.relationship('User', secondary=user_room_association, back_populates='rooms')


class Message(db.Model):
    id = db.Column(db.String(36), default=generate_uuid, primary_key=True) # Unique ID for message
    data = db.Column(db.String(5000)) # Max message characters
    user_id = db.Column(db.String(36), db.ForeignKey('user.id')) # User ID of message
    room_id = db.Column(db.String(36), db.ForeignKey('room.id')) # Room ID of message
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='messages')

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), default=generate_uuid, primary_key=True)
    username = db.Column(db.String(50), unique=True) # Username max 50 char
    nickname = db.Column(db.String(55), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) # E-Mail max 150 char
    password = db.Column(db.String(150), nullable=False) # Password max 150 char
    dob = db.Column(db.String(20),nullable=False) # Date object of DOB
    country = db.Column(db.String(150), nullable=False) # Country of user
    aboutme = db.Column(db.String(500))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    random_search_enabled = db.Column(db.Boolean, default=True)
    img = db.Column(db.String(350)) # img of user
    gender = db.Column(db.String(30)) # Gender
    rooms = db.relationship('Room', secondary=user_room_association, back_populates='users')
    admin_rooms = db.relationship('Room', secondary=admin_rooms_association, back_populates='admins')
    messages = db.relationship('Message', back_populates='user')

