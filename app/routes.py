from flask import Blueprint, request, jsonify
from flask_socketio import send, emit, join_room, leave_room
from functools import wraps
from . import socketio, db
from .models import User, Message
import jwt
import datetime

main = Blueprint('main', __name__)

# Basic route for the homepage
@main.route('/')
def index():
    return "Welcome to the Chat App"

# Token-based authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Handle user connecting to the chat
@socketio.on('join')
@token_required
def handle_join(current_user, data):
    username = current_user.username
    room = data['room']
    join_room(room)
    send(f'{username} has entered the room.', to=room)

# Handle user sending a message
@socketio.on('message')
@token_required
def handle_message(current_user, data):
    room = data['room']
    msg = data['message']
    username = current_user.username
    new_message = Message(username=username, room=room, message=msg)
    db.session.add(new_message)
    db.session.commit()
    emit('message', {'username': username, 'message': msg}, to=room)

# Handle user disconnecting
@socketio.on('leave')
@token_required
def handle_leave(current_user, data):
    username = current_user.username
    room = data['room']
    leave_room(room)