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

        # extract form data
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        username = request.form.get('username')
        password = request.form.get('password')
        shipping_address = request.form.get('shipping-address')
        billing_address = request.form.get('billing-address')

        # confirm password
        confirm_password = request.form.get('confirm-password')

        # check if passwords match
        if password != confirm_password:
            return render_template('register.html', msg="Passwords do not match.")

        # check if user exists
        user = User.query.filter_by(username=username).first()

        # if user does not exist, create user
        if not user:

            # check if all fields are filled
            if all([first_name, last_name, username, password, shipping_address, billing_address]):

                # create the user object
                new_user = User(username=username, password=generate_password_hash(password),
                                first_name=first_name, last_name=last_name, status='preferred',
                                shipping_address=shipping_address, billing_address=billing_address)
                
                # add user to the database
                db.session.add(new_user)
                db.session.commit()

                # redirect to login
                return redirect(url_for('auth.login'))
            
            else:

                # missing fields
                return render_template('register.html', msg="All fields are required.")
        else:

            # user already exists (return error)
            return render_template('register.html', msg="User already exists.")
        
    else:
        return render_template('register.html')
