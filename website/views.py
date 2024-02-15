from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, json, current_app
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, emit
from datetime import datetime, timedelta
from .functions import create_room, get_rooms_count, get_public_rooms, invite_code, calculate_age, upload_to_imgbb, is_valid_image, smiley_list, add_admins, get_admins, remove_admin, handle_command
from .models import Room, User, Message
from . import db, socketio
from better_profanity import profanity
import requests, bleach, os, time
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)
MAX_IMAGE_SIZE_MB = 10

# Enable HSTS for all routes
@views.after_request
def add_hsts_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    user = current_user.id
    name = current_user.nickname
    join_room(room_id)
    print(f'Client {user} | {name} joined room: {room_id}')

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data['room_id']
    leave_room(room_id)
    print(f'Client left room: {room_id}')

@socketio.on("new_message")
def handle_new_message(data):
    if current_user.is_authenticated:
        room_id = data['room_id']
        user = current_user
        message = data['message']
        message = bleach.clean(message, tags=['img', 'strong', 'em', 'u', 'b', 'mark', 'del', 'sub', 'sup'], attributes=['src', 'alt'])
        message = profanity.censor(message)
        name = current_user.nickname
        recipient_id = data.get('recipient_id')  # Add this line to get the recipient id from the client
        if message.startswith("/"):
            room = Room.query.get(room_id)  # Fetch the room object
            response_message = handle_command(message, room)
            img = "https://cdn.pixabay.com/photo/2018/11/13/21/43/avatar-3814049_1280.png"
            emit('message', {'msg': response_message, 'user': 'System', 'id': user.id, 'time_sent': "System", 'img': img}, room=room_id)
        elif recipient_id:
            # Handle private messages
            db_private_message = PrivateMessage(data=message, sender_id=user.id, recipient_id=recipient_id)
            db.session.add(db_private_message)
            db.session.commit()
        else:
            # Handle regular chat messages
            db_message = Message(data=message, user_id=user.id, room_id=room_id)
            # Add the message to the database
            db.session.add(db_message)
            db.session.commit()
            print(f"New message from {name} in room {room_id}: {str(message).encode('utf-8')}")
            time_sent = str(db_message.timestamp.strftime("%H:%M"))  # Format the timestamp nicely
            if not current_user.img:
                img = "https://cdn.pixabay.com/photo/2018/11/13/21/43/avatar-3814049_1280.png"
            else:
                img = current_user.img
            emit('message', {'msg': message, 'user': user.nickname, 'id': user.id, 'time_sent': time_sent, 'img': img}, room=room_id)  # Newly added 'time_sent' field to the output
    else:
        print("Error sending message")

#########################################################
@views.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    else:
        return render_template('index.html', user=current_user)
    
@views.route('/dashboard')
@login_required
def dashboard():
    public_rooms = get_public_rooms()
    my_rooms = current_user.rooms
    return render_template('dashboard.html', user=current_user, rooms=get_rooms_count(), public_rooms=public_rooms, my_rooms=my_rooms)

@views.route('/games')
def games():
    return render_template('games.html', user=current_user)

@views.route('/games/snake')
def games_snake():
    return render_template('/games/snake.html', user=current_user)

@views.route('/create', methods=['GET', 'POST'])
@login_required
def create_room_route():
    room_id, invite_code = None, None
    if current_user.is_authenticated:
        try:
            if request.method == 'POST':
                # Process form submission and create the room
                room_name = request.form.get('room_name')
                room_type = request.form.get('room_type')
                room_keywords = request.form.get('room_keywords')
                room_name = bleach.clean(room_name)
                room_keywords = bleach.clean(room_keywords)
                if room_type == 'is_private':
                    is_private = True
                else:
                    is_private = False
                # Create room and get the room ID and invite code
                room_id, invite_code = create_room(room_name=room_name, is_private=is_private, admin_id=current_user.id, description=room_keywords)
                flash(f'🎉 Room <strong>{room_name}</strong> created successfully! <strong>Code: {invite_code}</strong>', category='success')
                # Redirect with parameters directly in the URL
                return redirect(url_for('views.join_room_route', room_id=room_id))
            # This return statement was missing
            return render_template('create.html', room_id=room_id, invite_code=invite_code, user=current_user)
        except Exception as e:
            print("OHH NOOO --!!!--:", e)
            
@views.route('/join_room/<string:room_id>', methods=['GET', 'POST'])
@login_required
def join_room_route(room_id):
    invite_code = request.args.get('invite_code')
    room = Room.query.get(room_id)
    if room.is_private:
        flash('Room is private. You need to join via invite code or link!', category='error')
        return redirect(url_for('views.dashboard'))
    elif room:
        # Check if the user is already associated with the room
        if current_user in room.users:
            return redirect(url_for('views.chat', room_id=room_id))
        else:
            room.users.append(current_user)
            db.session.commit()
            return redirect(url_for('views.chat', room_id=room_id))
    else:
        flash('Room not found.', category='error')
    return redirect(url_for('views.dashboard'))

@views.route('/leave_room/<string:room_id>', methods=['GET', 'POST'])
@login_required
def leave_room_route(room_id):
    room = Room.query.get(room_id)
    if current_user in room.users:
        room.users.remove(current_user)
        db.session.commit()
        flash(f'You have left the room: {room.room_name}', category='success')
    else:
        flash(f'You are not in the room: {room.room_name}', category='warning')
    return redirect(url_for('views.dashboard'))

@views.route('/edit/<string:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = Room.query.get(room_id)
    
    if current_user in room.admins or current_user.id == room.admin_id:
        if request.method == 'POST':
            if 'save_changes' in request.form:
                # Update room details based on form data
                room.room_name = request.form.get('room_name')
                room.is_private = 'is_private' in request.form
                room.description = request.form.get('description')
                room.invite_code = request.form.get('generate_code')     
                db.session.commit()
                flash("Room details updated successfully!", category="success")
                return redirect(url_for('views.edit_room', room_id=room_id))
            elif 'add_admin' in request.form:
                new_admin_ids = request.form.getlist('new_admin_ids')
                add_admins(room, new_admin_ids)
                flash("Admins added!", category="success")
                db.session.commit()
            elif 'remove_admin' in request.form:
                admin_id_to_remove = request.form.get('admin_id_to_remove')
                remove_admin(room, admin_id_to_remove)
                flash("Admins removed!", category="success")
                db.session.commit()
            return redirect(url_for('views.edit_room', room_id=room_id))
        return render_template('edit_room.html', user=current_user, room=room, admins=get_admins(room))
    else:
        flash("No access!", category="error")
        return redirect(url_for('views.edit_room', room_id=room_id))

@views.route('/chat/<string:room_id>', methods=['GET', 'POST'])
@login_required
def chat(room_id):
    room = Room.query.get(room_id)
    if current_user in room.users:
        # Fetch message history from the database
        message_history = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp).all()
        users = room.users
        # Handle user search
        search_term = request.args.get('search', '').lower()
        if search_term:
            users = [user for user in users if search_term in user.nickname.lower()]
        return render_template('chat.html', user=current_user, room=room, message_history=message_history, users=users, search_term=search_term, smileys=smiley_list())
    else:
        flash(f'You have not joined this room!', category='error')
        return redirect(url_for('views.index'))

@views.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    if request.method == 'POST':
        invite_code = request.form.get('invite_code')
        room = Room.query.filter_by(invite_code=invite_code).first()
        if room:
            # Add the user to the room
            room.users.append(current_user)
            db.session.commit()
            flash(f'Successfully joined room: {room.room_name}', 'success')
            return redirect(url_for('views.join_room_route', room_id=room.id))  # Redirect to join_room_route
        flash('Invalid invite code. Please try again.', 'error')
        return render_template('join.html', user=current_user)
    return render_template('join.html', user=current_user)
    
@views.route('/generate_invite_code', methods=['GET'])
@login_required
def generate_invite_code():
    invite = invite_code()
    return jsonify(invite_code=invite)

@views.route('/view_profile/<string:user_id>', methods=['GET'])
@login_required
def view_profile(user_id):
    user_profile = User.query.get(user_id)
    if user_profile:
        age = calculate_age(user_profile.dob)
        return render_template('view_profile.html', user=current_user, user_profile=user_profile, age=age)
    else:
        flash('User not found.', category='error')
        return redirect(url_for('views.dashboard'))
    
@views.route('/get_gifs/<string:search_term>')
def get_gifs(search_term):
    try:
        with open('chatapp/config.json', 'r') as config_file:
            config = json.load(config_file)
        key = config["GIPHY_API_KEY"]
        link = f'https://api.giphy.com/v1/gifs/search?api_key={key}&q={search_term}&limit=25'
        response = requests.get(link)
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the relevant data from the Giphy API response
            data = response.json().get('data', [])
            # Extracting URLs from the response
            gif_urls = [item.get('images', {}).get('fixed_height', {}).get('url', '') for item in data]
            return jsonify({'gifs': gif_urls})
        else:
            return jsonify({'error': 'Failed to fetch GIFs from Giphy API'})
    except Exception as e:
        return jsonify({'error': str(e)})

@views.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file:
            if image_file.content_length > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                flash(f'File size exceeds the maximum allowed ({MAX_IMAGE_SIZE_MB} MB).', category='error')
                return jsonify({'error': 'File size exceeds the maximum allowed.'})
            # Save the image file to the designated upload folder
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            try:
                is_valid_image(image_path)
                imgbb_url = upload_to_imgbb(image_path)
            except Exception as e:
                print(e)
            os.remove(image_path)
            if imgbb_url:
                return jsonify({'image': imgbb_url})
            else:
                flash('Failed to upload image to ImgBB.', category='error')
        else:
            flash('Failed to upload image to ImgBB.', category='error')
            
@views.route('/dm/<string:recipient_id>', methods=['GET', 'POST'])
@login_required
def dm_view(recipient_id):
    recipient = User.query.get(recipient_id)
    if not recipient:
        flash("Recipient not found.", category="error")
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        message_content = request.form.get('message_content')
        if message_content:
            send_private_message(current_user, recipient, message_content)

    private_messages = get_private_messages(current_user, recipient)
    return render_template('dm.html', recipient=recipient, private_messages=private_messages)