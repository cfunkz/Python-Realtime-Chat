from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Room
from .functions import generate_funny_nickname, upload_to_imgbb
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os


auth = Blueprint('auth', __name__)

# Enable HSTS for all routes
@auth.after_request
def add_hsts_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    else:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter(or_(User.username == username, User.email == username)).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in succesfully!', category='success')
                    login_user(user, remember=True) # Login user and remember session
                    return redirect(url_for('views.dashboard'))
                else:
                    flash('Incorrect password.', category='error')
            else:
                flash('No user found.', category='error')
        return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('newUsername')
        email = request.form.get('newEmail')
        password = request.form.get('newPassword')
        password2 = request.form.get('newPassword2')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        country = request.form.get('country')
        user = User.query.filter_by(username=username).first()
        user_mail = User.query.filter_by(email=email).first()
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        age = relativedelta(datetime.now(), dob_date).years

        if user:
            flash('Username taken.', category='error')
        elif user_mail:
            flash('E-Mail taken.', category='error')
        elif len(username) < 3:
            flash('Username must be at least 3 characters long!', category='error')
        elif len(email) < 4:
            flash('Wrong e-mail format.', category='error')
        elif password != password2:
            flash('Passwords dont match!', category='error')
        elif len(password) < 6:
            flash('Password must have at least 6 characters!', category='error')
        elif age < 18:
            flash('You must be 18+ to join.', category='error')
        elif len(country) < 0:
            flash('Please select a your country!', category='error')
        else:
            new_user = User(username=username, nickname=generate_funny_nickname(), email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), dob=dob, gender=gender, country=country)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) # Login user and remember session
            flash('Account created!', category='success')
            return redirect(url_for('views.dashboard'))
    return render_template('login.html', user=current_user)


@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        image_file = request.files.get('image')
        new_username = request.form.get('username')
        new_username2 = request.form.get('username2')
        new_nickname = request.form.get('nickname')
        new_dob = request.form.get('dob')
        new_country = request.form.get('country')
        old_password = request.form.get('oldpassword')
        new_password = request.form.get('password')
        new_password2 = request.form.get('password2')
        new_about_me = request.form.get('aboutme')
        new_email = request.form.get('email')
        
        if image_file:
            # Save the image file to the designated upload folder
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            # Upload to ImgBB and get the image URL
            imgbb_url = upload_to_imgbb(image_path)
            if imgbb_url:
                # Update the user's image URL in the database
                current_user.img = imgbb_url
                flash('Image uploaded and link saved successfully!', category='success')
            else:
                flash('Failed to upload image to ImgBB.', category='error')
        
        # Validate and update the user details
        elif new_username:
            if new_username != new_username2:
                flash('Usernames dont match.', category='error')
            elif len(new_username) < 3:
                flash('Username must be at least 3 characters long!', category='error')
            else:
                current_user.username = new_username
                flash('Username updated successfully!', category='success')
        
        # Nickname
        elif new_nickname:
            if len(new_nickname) < 3:
                flash('Username must be at least 3 characters long!', category='error')
            else:
                current_user.nickname = new_nickname
                flash('Nickname updated successfully!', category='success')
                
                
        #DATE OF BIRTH
        elif new_dob:
            dob_date = datetime.strptime(new_dob, '%Y-%m-%d')
            age = relativedelta(datetime.now(), dob_date).years
            if age < 18:
                flash('You must be 18+ to join.', category='error')
            else:
                current_user.dob = new_dob
                flash('Date of birth updated successfully!', category='success')
                
                
        #COUNTRY
        elif new_country:
            current_user.country = new_country
            flash('Country updated successfully!', category='success')
            
            
        #NEW PASSWORD
        elif new_password:
            if check_password_hash(current_user.password, old_password):
                if len(new_password) < 6:
                    flash('Password must have at least 6 characters!', category='error')
                elif new_password != new_password2:
                    flash('Passwords must match!', category='error')
                else:
                    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                    flash('Password updated successfully!', category='success')
            else:
                flash('Wrong password!', category='error')


        #About Me
        elif new_about_me:
            if len(new_about_me) > 500:
                flash('Max 500 characters long!', category='error')
            else:
                current_user.aboutme = new_about_me
                flash('About me updated successfully!', category='success')


        elif new_email:
            user_mail = User.query.filter_by(email=new_email).first()
            if len(new_email) < 4:
                flash('Wrong e-mail format.', category='error')
            elif user_mail:
                flash('E-Mail taken.', category='error')
            else:
                current_user.email = new_email
                flash('Email updated successfully!', category='success')

        db.session.commit()
        return redirect(url_for('auth.settings'))
    
    return render_template('settings.html', user=current_user)

