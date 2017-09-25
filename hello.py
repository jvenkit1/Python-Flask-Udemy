import os
from flask import Flask, url_for, request, render_template, redirect, flash, make_response, session
import logging
from logging.handlers import RotatingFileHandler
import pymysql
import ConfigParser

app = Flask(__name__)

@app.route('/',) # This is the Index Page and redirects to the login page.
def welcome():
    if 'username' in session :
        return render_template('welcome.html', username = session['username'])
    else :
        return redirect(url_for('login'))

@app.route('/username/<username>') # Prints the name of the user logged in.
def ret_user(username):
    # Returns the User Profile for the Given user
    return 'User %s logged in' % username

@app.route('/post/<int:post_id>') # Returns the Post ID of the user logged in. This enforces that the input be an Integer.
def ret_post(post_id):
    # Returns the Post id
    return 'Post id is %d' % post_id

@app.route('/login', methods = ['GET','POST']) # The Core functionality - Login functionality
def login():
    error = None # Initializing the error message as Null.
    if request.method == 'POST': # If the user submits a form, i.e requests a Post method by providing some information the following occurs.
        if validate_user(request.form['username'],request.form['password']) == True: # Validating if the correct user is logged in
            flash("Login successful") # Using Flash Messages
            session['username'] = request.form.get('username') # We use Sessions to store the user login info.
            return redirect(url_for('welcome'))
        else :  # The ID and Password entered by the user is incorrect.
            error = 'Incorrect Username/Password'
            app.logger.warning('Incorrect Username / Password for user %s', request.form.get('username'))
            return redirect(url_for('login'))
    else :
        return (render_template('login.html', error = error)) #Redirects to the Login Page as Null input was provided.


@app.route('/logout', methods = ['GET', 'POST']) # Logout functionality
def logout():
    if request.method == 'POST':
        session.pop('username', None) # Deleting the session
        return redirect(url_for('login'))

def validate_user(username, pwd): # We validate the user with the information stored in a Local Database. If the record exists, the user is valid.

    config = ConfigParser.RawConfigParser() # Using Properties file.
    config.read('ConfigFile.properties')
    # Setting Values to the Default variables.
    MYSQL_DATABASE_HOST = os.getenv(config.get('DatabaseSection', 'database.dbIP'),config.get('DatabaseSection', 'database.dbHost'))
    MYSQL_DATABASE_USER = config.get('DatabaseSection', 'database.dbuser')
    MYSQL_DATABASE_PASSWORD = config.get('DatabaseSection', 'database.dbpwd')
    MYSQL_DATABASE_DB = config.get('DatabaseSection','database.dbname')

    # Establishing a Connection with the Database.
    conn = pymysql.connect(host = MYSQL_DATABASE_HOST, user = MYSQL_DATABASE_USER, password = MYSQL_DATABASE_PASSWORD, db = MYSQL_DATABASE_DB)
    cursor = conn.cursor()
    # We check if the value entered by the user is present in the DB. If the value is not present, data will hold NULL Values.
    cursor.execute("SELECT * FROM user WHERE user_name = '%s' AND password = '%s'" % (username, pwd))

    data = cursor.fetchone()

    if data :
        return True

    return False

if __name__ == '__main__':

    host = os.getenv('IP','127.0.0.1') # Setting the Environment Variables
    port = int(os.getenv('PORT',5800)) # Setting the Port Number
    app.debug = True # This allows us to debug the applications on the go
    app.secret_key = os.urandom(24) # Setting a Random Secret Key value.

    # Logger
    handler = RotatingFileHandler('error.log', maxBytes = 10000, backupCount = 1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    
    app.run(host = host, port = port)
