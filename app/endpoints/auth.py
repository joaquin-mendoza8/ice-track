from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
# hash password
from werkzeug.security import generate_password_hash, check_password_hash

# TODO: enforce strong passwords

# create the auth blueprint
auth = Blueprint('auth', __name__)

# create the login endpoint
@auth.route('/login', methods=['GET', 'POST'])
def login():

    # get message from query string
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type')

    if request.method == 'POST':

        # get username/pw from form
        username = request.form.get('username')
        password = request.form.get('password')

        # process login
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            
            # login the user
            login_user(user)

            # redirect to home
            return redirect(url_for('home.home_home'))

        else:

            # invalid credentials
            return render_template('auth/login.html', msg="Invalid credentials provided."), 400
        
    else:

        # render the login page (GET request)
        return render_template('auth/login.html', msg=msg, msg_type=msg_type), 200
    

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

        msg, msg_type = None, None

        # extract form data
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        username = request.form.get('username')
        password = request.form.get('password')
        shipping_address = request.form.get('shipping-address')
        billing_address = request.form.get('billing-address')

        # confirm password
        confirm_password = request.form.get('confirm-password')

        # package the data into a dictionary to pass back to the form
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'shipping_address': shipping_address,
            'billing_address': billing_address
        }

        # check if passwords match
        if password != confirm_password:
            msg = "Passwords do not match."
        
        # check if all password criteria are met
        if len(password) < 8: # password must be at least 8 characters long
            msg = "Password must be at least 8 characters long."
        if len(password) > 20: # password must be less than 20 characters long
            msg = "Password must be less than 20 characters long."
        allowed_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '+', '=']
        for char in password: # password can only contain allowed characters, numbers, and letters
            if (char not in allowed_chars and
                not char.isnumeric() and 
                not char.isalpha()):
                msg = (f"Password can only contain numbers, letters, and special characters ({''.join(allowed_chars)}).")

        # return error message if any
        if msg:
            return render_template('auth/register.html', msg=msg, **data)

        # check if user exists
        user = User.query.filter_by(username=username).first()

        # if user does not exist, create user
        if not user:

            # create the user object
            new_user = User(username=username, password=generate_password_hash(password),
                            first_name=first_name, last_name=last_name, status='preferred',
                            shipping_address=shipping_address, billing_address=billing_address)
            
            # add user to the database
            db.session.add(new_user)
            db.session.commit()

            # log the successful registration
            print(f"User {username} successfully registered.")
            msg = (f"User {username} successfully registered.")

            # redirect to login
            return redirect(url_for('auth.login', msg=msg, msg_type='success'))

        else:

            # user already exists (return error)
            return render_template('auth/register.html', msg="User already exists."), 400

    # render the register page (GET request)
    return render_template('auth/register.html')
