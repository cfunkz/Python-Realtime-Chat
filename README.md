# EchoChat

This is a simple Flask-based chat application with basic features. There are plans add more features and improvements.

## Images

<img width="1277" alt="login" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/79a8d509-27f1-4932-897b-f8a411e72f8f">
<img width="1280" alt="register" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/9af9f5cb-8a4e-4581-8a58-634a069ec35a">
<img width="1271" alt="dash" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/7ab24f42-92ed-4de7-8ad8-02de426d6290">
<img width="1280" alt="create" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/7a39b3cd-3be1-40c7-a810-2f70b4408795">
<img width="1279" alt="join" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/51b90d2a-c26e-4aa6-b680-559da7b39b55">
<img width="1280" alt="edit" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/a70e57f7-2467-407a-87b8-17c9c61718b6">
<img width="1267" alt="descript" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/79799990-d7a1-4354-bbab-e81328989259">
<img width="1278" alt="chat" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/0a616f8f-7731-42d0-a15d-77d6084c8b2b">
<img width="1280" alt="gifs" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/beb85da7-8172-4e7f-82f2-43b792441f63">
<img width="1279" alt="user-list" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/12bc371e-9149-43ce-9648-3c624df7352b">
<img width="1274" alt="view" src="https://github.com/cfunkz/Python-Web-Chat/assets/116670695/391634de-c2cc-4a81-a66b-bc75dda94e0d">

## Dependencies

- [Flask](https://flask.palletsprojects.com/) - Web framework for Python
- [Flask-Login](https://flask-login.readthedocs.io/) - User session management for Flask
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and Object-Relational Mapping (ORM)
- [SQLite](https://www.sqlite.org/) - Embedded relational database engine
- [Requests](https://docs.python-requests.org/en/latest/) - HTTP library for Python
- [Bleach](https://bleach.readthedocs.io/) - An HTML sanitization library
- [Better Profanity](https://github.com/snguyenthanh/better_profanity) - A profanity filter library
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - WebSocket support for Flask applications
- [Pillow (PIL Fork)](https://pillow.readthedocs.io/) - Python Imaging Library (PIL Fork)

### Features
- [x] Basic Input Validation, Sanitazion & CSPS/HSTS
- [x] Login / Register
- [x] Basic Dashboard
- [x] Emojis
- [x] Gif sharing using `Giphy`
- [x] Image uploading, Image sending using `IMGBB`
- [x] Create Room, Join Room, Edit Room, Leave Room, Private Rooms, User List
- [x] SQLite Database
- [x] Working HTML tags in messages `<b>bold</bold>, <img>` etc. and "``" for embed.
- [X] Admin list with admin panel for managing users

### To-Do List
- [ ] Room search
- [ ] Notification system & private messages
- [ ] Stream Video (one to one, one to many)
- [ ] Online Users
- [ ] GMAIL SMTP
- [ ] Voice record & transcribe?

## How to use

1. Download/Clone repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your keys and variables in `config.json`.
4. Run the application with `python app.py`.
5. Visit `http://localhost:5000` in your web browser.
