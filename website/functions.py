from faker import Faker
import random, requests, json, string, secrets
from datetime import datetime
from . import db
from .models import Room, User
from PIL import Image

def smiley_list():
    return [
        '😊', '😄', '😃', '😁', '👀', '😆', '😅', '😂', '🤣', '😇', '🥳', '🥴', '🤤', '😍', '🥰', '😘', '👅', '💋', '🫦',
        '❤️', '🖤', '💘', '💖', '💞', '❤️‍🔥', '❤️‍🩹', '💌', '🙈', '🙉', '🙊', '😋', '😎', '🤩', '😜',
        '😝', '😌', '😏', '😒', '😓', '😔', '😖', '😞', '😟', '😠', '😡', '🤬', '🥺', '😢', '😭', '😤', '😥',
        '😦', '😧', '😨', '😩', '🤯', '😱', '😳', '🥵', '🥶', '😱', '😭', '😤', '😥', '😦', '😧', '😨', '🤯', 
        '😰', '🥷', '💯', '💦', '👁️', '🛌', '🛀', '🐒', '💥', '💢', '💣', '💤','🦍', '🦧', '🐺', '🦊', '🦝',
        '🐸', '🐱', '🐈', '🦖', '🦕', '🐢', '🐳', '🐋', '🐬', '🦭', '🐟',
        '🍀', '🌿', '🍁', '🍇', '🍉', '🍆', '🥑', '🍑', '🥓', '🍔',
        '🍟', '🍕', '🍿', '🌭', '🍒', '🥝', '🍓', '🫐', '🥥', '🥦', '🍄', '🍺', '🍻', '🍾', '🥂', '🧉', '🧊',
        '🍷', '🎂', '🍦', '🍩', '🎉', '🎊', '🎁', '🎗️', '☕', '🍽️', '🍴', '🫶', '👋', '🖐️', '✋', '🖖', '🫱',
        '🫲', '🫳', '🫴', '👌', '🤌', '👃', '🤏', '✌️', '🫰', '🤞', '🤟', '🤘', '🤙', '🫵', '👍', '👎', '👂',
        '🦻', '🦼', '🦽', '🦾']

def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            # Check if the file is a valid image
            img.verify()
            return True
    except Exception as e:
        print(f"Invalid image: {e}")
        return False
    
def calculate_age(date_of_birth):
    current_date = datetime.now().date()
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date() if isinstance(date_of_birth, str) else date_of_birth
    age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
    return age


def upload_to_imgbb(file_path):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    imgbb_api_key = config['IMGBB_KEY']
    endpoint = "https://api.imgbb.com/1/upload"
    with open(file_path, "rb") as file:
        files = {"image": file}
        params = {"key": imgbb_api_key}
        response = requests.post(endpoint, params=params, files=files)
        if response.status_code == 200:
            result = response.json()
            return result['data']['url']
        else:
            return None

def invite_code():
    characters = string.ascii_uppercase + string.digits
    invite_code = ''.join(secrets.choice(characters) for _ in range(10))
    return invite_code

def create_room(room_name, is_private=False, admin_id=None, description=None):
    characters = string.ascii_uppercase + string.digits
    invite_code = ''.join(secrets.choice(characters) for _ in range(10))
    admin_user = User.query.get(admin_id)
    room = Room(room_name=room_name, is_private=is_private, invite_code=invite_code, admin=admin_user, description=description)
    db.session.add(room)
    db.session.commit()
    return room.id, invite_code

def generate_funny_nickname():
    fake = Faker()
    prefixes = [
        "Happy", "Silly", "Clever", "Cheery", "Witty", "Whimsy",
        "Goofy", "Jolly", "Amuse", "Joyful", "Zany", "Pecu",
        "Droll", "Lively", "Mirth", "Quirky", "Light", "Playful",
        "Merry", "Frolic", "Entert", "Jovial", "Jocular", "Bubbly",
        "Waggis", "Humor", "Spiri", "Laugh", "Grin", "Merry",
        "Ludicr", "Zest", "Animat", "Chipper", "Ecstat", "Giddy",
        "Delight", "Jesting", "Tickle", "Ridic", "Jabber", "Surreal",
        "Fantas", "Giggly", "Flippan", "Zippy", "Snazzy"
    ]
    prefix = random.choice(prefixes)
    text = fake.word()
    nr = random.randint(1, 99)
    suffixes = [
        "Peng", "Banana", "Squir", "Bubble", "Noodle", "Muff",
        "Cupcake", "Snicker", "Tootsie", "Bumble", "Butter", "Whisp",
        "Bamboo", "Doodle", "Moon", "Lolly", "Sasq", "Gizmo",
        "Pickle", "Popcorn", "Chuckle", "Giggle", "Sunflow", "Marsh",
        "Sunny", "Peach", "Pumpkin", "Twink", "Peachy", "Rain",
        "Sizzle", "Dizzy", "Chirpy", "Squigg", "Bumble", "Glimmer",
        "Dazzle", "Zigzag", "Dizzy", "Fluffy", "Flutter", "Snicker"
    ]
    suffix = random.choice(suffixes)
    # Combine to form the nickname
    nickname = f"{prefix}{text.title()}{suffix}{nr}"
    nickname = nickname.replace(".", "")
    return nickname

def get_rooms_count():
    all_rooms = Room.query.all()
    num_rooms = len(all_rooms)
    return num_rooms


def get_public_rooms():
    public_rooms = Room.query.filter_by(is_private=False).all()
    return public_rooms

#########################admin stuff###########################
def is_admin(user_id, room_id):
    # Check if the user with user_id is an admin in the specified room_id
    room = Room.query.filter_by(id=room_id).first()
    if room:
        admin = User.query.filter_by(id=user_id).first()
        return admin and admin.id == room.admin_id
    return False

# Function to add new admins to the room
def add_admins(room, new_admin_ids):
    existing_admin_ids = [admin.id for admin in room.admins]
    for admin_id in new_admin_ids:
        admin_id = admin_id.strip()
        if len(admin_id) == 36 and admin_id not in existing_admin_ids:
            user = User.query.get(admin_id)
            if user:
                room.admins.append(user)

def remove_admin(room, admin_id):
    admin_to_remove = User.query.get(admin_id)
    if admin_to_remove in room.admins:
        room.admins.remove(admin_to_remove)
        db.session.commit()

def get_admins(room):
    if room.admins:
        return room.admins # Returns admins as list of user objects [<user_id>]
    else:
        return None
    
def handle_command(command, room):
    command = command.lower()  # Convert the command to lowercase
    if command.startswith("/admins"):
        admins_list = get_admins(room)
        if admins_list:
            admin_names = [admin.nickname for admin in admins_list]
            response_message = f"Admins in the room: {', '.join(admin_names)}"
        else:
            response_message = "There are no admins in the room."
        return response_message