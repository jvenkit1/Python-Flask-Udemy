import os
from flask import Flask, url_for, request, render_template, redirect, flash, make_response, session
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)


@app.route('/hello')
@app.route('/hello/<username>')
def hello_world(name = None):
    return render_template('trial.html', name = name)

@app.route('/username/<username>')
def ret_user(username):
    # Returns the User Profile for the Given user
    return 'User %s logged in' % username

@app.route('/post/<int:post_id>')
def ret_post(post_id):
    # Returns the Post id
    return 'Post id is %d' % post_id

@app.route('/login', methods = ['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if validate_user(request.form['username'],request.form['password']) == True:
            flash("Login successful")
            session['username'] = request.form.get('username')
            return redirect(url_for('welcome'))
        else :
            error = 'Incorrect Username/Password'
            app.logger.warning('Incorrect Username / Password for user %s', request.form.get('username'))
            return redirect(url_for('login'))
    else :
        return (render_template('login.html', error = error))

@app.route('/',)
def welcome():
    if 'username' in session :
        return render_template('welcome.html', username = session['username'])
    else :
        return redirect(url_for('login'))

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect(url_for('login'))

def validate_user(username, password):
    if username == password:
        return True
    return False

if __name__ == '__main__':
    host = os.getenv('IP','127.0.0.1')
    port = int(os.getenv('PORT',5101))
    app.debug = True
    app.secret_key = os.urandom(24)

    # Logger
    handler = RotatingFileHandler('error.log', maxBytes = 10000, backupCount = 1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host = host, port = port)
