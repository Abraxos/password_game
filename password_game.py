'''A webapp that makes game for kids to guess passwords. The admin interface
   allows you to choose a character whose password needs to be guessed'''
from logging.handlers import RotatingFileHandler
from logging import INFO
from configparser import ConfigParser
from collections import namedtuple

from flask import Flask
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField

# Constants
APP_NAME = 'Password Game'
PASSWD_FILE_KEY = 'password_file'
USERNM_FILE_KEY = 'username_file'
ATTEMPTS_FILE_KEY = 'attempts_file'
LOG_FILE_KEY = 'log_file'
PORT_KEY = 'port'
CONFIG_PATH = 'config.ini'

APP = Flask(APP_NAME)
APP.secret_key = 'debug key'
CONFIG = ConfigParser()

User = namedtuple('User', ['username', 'name', 'mother_maiden_name',
                           'date_of_birth', 'hint', 'hobbies', 'password',
                           'name_of_pet', 'favorite_color',
                           'favorite_sports_team'])
Attempt = namedtuple('Attempt', ['username', 'password'])

def get_attempts():
    '''Returns the contents of the attempts file as a list of objects.'''
    attempts = []
    with open(CONFIG[APP_NAME][ATTEMPTS_FILE_KEY], 'r') as attempts_file:
        for line in attempts_file.readlines():
            username = line.split(' : ', 1)[0]
            password = line.split(' : ', 1)[1]
            attempts.append(Attempt(username=username, password=password))
    if attempts:
        return reversed(attempts)
    else:
        return None

def get_prop(user, prop):
    '''Accessor for a property of a particular user.'''
    if user in CONFIG:
        if prop in CONFIG[user]:
            return CONFIG[user][prop]
    else:
        return ''

def get_user(username):
    '''Retrieves information about a user and packs it as a namedtuple.'''
    if username in CONFIG:
        user = User(username=username,
                    name=get_prop(username, 'name'),
                    password=get_prop(username, 'password'),
                    mother_maiden_name=get_prop(username, "mother's maiden name"),
                    date_of_birth=get_prop(username, 'date of birth'),
                    hint=get_prop(username, 'hint'),
                    hobbies=get_prop(username, 'hobbies'),
                    name_of_pet=get_prop(username, 'name of pet'),
                    favorite_color=get_prop(username, 'favorite color'),
                    favorite_sports_team=get_prop(username, 'favorite sports team'))
        return user

@APP.route('/view/')
def view():
    '''Displays a list of available users with links to select them.'''
    usernames = [u for u in CONFIG if u not in [APP_NAME, 'DEFAULT']]
    return render_template('view.html', users=[get_user(u) for u in usernames])

@APP.route('/view/<string:username>')
def view_username(username):
    '''Displays the details of a single user.'''
    if username in CONFIG:
        return render_template('view_username.html', user=get_user(username))
    else:
        return "No such user!"


class LoginForm(FlaskForm):
    '''A simple login form for the user to guess passwords'''
    username = StringField('username')
    password = PasswordField('password')
    login_button = SubmitField('Login')

@APP.route('/login/')
def login():
    '''Presents the user with a login page.'''
    return render_template('login.html', form=LoginForm(),
                           attempts=get_attempts())

def username_passwd_correct(candidate_username, candidate_password):
    '''Checks whether the username and password are correct.'''
    with open(CONFIG[APP_NAME][PASSWD_FILE_KEY], 'r') as passwd_file:
        actual_password = passwd_file.read()
    with open(CONFIG[APP_NAME][USERNM_FILE_KEY], 'r') as usernm_file:
        actual_username = usernm_file.read()
    APP.logger.debug("Checking:\n\tUsername: {} ? {}\n\tPassword: {} ? {}"
                     .format(candidate_username, actual_username,
                             candidate_password, actual_password))
    return candidate_username == actual_username and \
           candidate_password == actual_password

@APP.route('/login_result/', methods=['GET', 'POST'])
def login_result():
    '''Informs the user that they have successfully logged in.'''
    APP.logger.debug('Computing login result')
    candidate_username = request.form['username']
    candidate_password = request.form['password']
    if username_passwd_correct(candidate_username, candidate_password):
        with open(CONFIG[APP_NAME][ATTEMPTS_FILE_KEY], 'w+') as attempts_file:
            attempts_file.write('')
        return render_template('login_successful.html')
    else:
        with open(CONFIG[APP_NAME][ATTEMPTS_FILE_KEY], 'a+') as attempts_file:
            attempts_file.write("{} : {}\n".format(candidate_username,
                                                 candidate_password))

        return render_template('login_failure.html', form=LoginForm(),
                               attempts=get_attempts())

@APP.route('/admin/')
def admin():
    '''Displays a list of available users with links to set their passwords as
       the current password.'''
    usernames = [u for u in CONFIG if u not in [APP_NAME, 'DEFAULT']]
    return render_template('admin.html', users=[get_user(u) for u in usernames])

@APP.route('/set_user/<string:username>')
def set_user(username):
    '''Sets the user and password for the current round of the game'''
    with open(CONFIG[APP_NAME][PASSWD_FILE_KEY], 'w+') as passwd_file:
        passwd_file.write(CONFIG[username]['password'])
    with open(CONFIG[APP_NAME][USERNM_FILE_KEY], 'w+') as usernm_file:
        usernm_file.write(username)
    APP.logger.info("SETTING - Username: {} Password: {}"\
                    .format(username, CONFIG[username]['password']))
    return redirect(url_for('admin'))

def parse_configuration(config_path):
    '''Parses a given configuration file and updates the global CONFIG.'''
    CONFIG.read(config_path)

def main():
    '''Main function, loads config, initializes logging, starts the app.'''
    parse_configuration(CONFIG_PATH)
    handler = RotatingFileHandler(CONFIG[APP_NAME][LOG_FILE_KEY],
                                  maxBytes=10000, backupCount=1)
    handler.setLevel(INFO)
    APP.logger.addHandler(handler)
    APP.run(port=int(CONFIG[APP_NAME][PORT_KEY]), debug=True)

if __name__ == '__main__':
    main()
