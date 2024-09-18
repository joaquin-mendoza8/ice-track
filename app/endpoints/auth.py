from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from config.config import db
from app.models import User
# hash password
from werkzeug.security import generate_password_hash, check_password_hash

# create the auth blueprint
auth = Blueprint('auth', __name__)

# create the login endpoint
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        # get username/pw from form
        username = request.form['username']
        password = request.form['password']

        # process login
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            
            # login the user
            login_user(user)

            # get the 'next' param from the request
            next_page = request.args.get('next')

            # redirect to home
            return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
        else:
            return render_template('login.html', msg="Invalid credentials provided.")
        
    else:
        return render_template('login.html')
    

# create the logout endpoint
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# create the register endpoint
@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # get username/pw from form
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # if user does not exist, create user
        if not user:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register.html', msg="User already exists.")
        
    else:
        return render_template('register.html')
