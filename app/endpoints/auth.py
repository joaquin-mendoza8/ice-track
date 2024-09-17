from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from config.config import db, session
from app.models import User
# hash password
from werkzeug.security import generate_password_hash, check_password_hash

# create the auth blueprint
auth = Blueprint('auth', __name__, template_folder='public/templates', static_folder='public/static')

# create the login endpoint
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        # get username/pw from form
        username = request.form['username']
        password = request.form['password']

        # check if user exists
        user = User.query.filter_by(username=username).first()

        # if user exists and password is correct, log user in
                # check if user exists
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            
            # login the user
            login_user(user)

            # set session user_id
            if user.id:
                session['user_id'] = user.id

            # redirect to home
            return redirect(url_for('home'))
        else:
            return render_template('login.html', msg="Invalid credentials provided.")
        
    else:
        return render_template('login.html')
    

# create the logout endpoint
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


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
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register.html', msg="User already exists.")
        
    else:
        return render_template('register.html')
