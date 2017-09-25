import os
from flask import Flask, url_for, request, render_template, redirect, flash, make_response, session
import logging
from logging.handlers import RotatingFileHandler
import pymysql
import ConfigParser

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

def validate_user(username, pwd):

    config = ConfigParser.RawConfigParser()
    config.read('ConfigFile.properties')
    #print config.get('DatabaseSection', 'database.dbname');
    MYSQL_DATABASE_HOST = os.getenv(config.get('DatabaseSection', 'database.dbIP'),config.get('DatabaseSection', 'database.dbHost'))
    MYSQL_DATABASE_USER = config.get('DatabaseSection', 'database.dbuser')
    MYSQL_DATABASE_PASSWORD = config.get('DatabaseSection', 'database.dbpwd')
    MYSQL_DATABASE_DB = config.get('DatabaseSection','database.dbname')
    print MYSQL_DATABASE_DB, MYSQL_DATABASE_HOST, MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD
    conn = pymysql.connect(host = MYSQL_DATABASE_HOST, user = MYSQL_DATABASE_USER, password = MYSQL_DATABASE_PASSWORD, db = MYSQL_DATABASE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user_name = '%s' AND password = '%s'" % (username, pwd))
    print username, pwd
    data = cursor.fetchone()
    if data:
        print 'True'
        return True
    print 'False'
    print data
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
