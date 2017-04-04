# Password Game

A hacking game for little kids allowing then to try to "hack" into a login page given some information about the users

## Disclaimer

This is a hacking game for little kids. The word "insecure" does not even begin to describe this webapp. If you use any component of this website as an example of security in any way, shape, or form, you have only yourself to blame.

## Setup

It is recommended that this game be set up in a virtual environment like so:

```
$ git clone git@github.com:Abraxos/password_game.git
$ cd password_game
$ mkdir .password_game_venv
$ virtualenv -p /usr/local/bin/python3.5 .password_game_venv # or wherever you have the python 3.5 binary
```

Activate the environment and install pre-requisite packages:

```
$ . .password_game_venv/bin/activate
(.password_game_venv) $ pip install flask flask_wtf
```

## Usage

Once you have the environment set up per instructions above, you can launch the webapp through the following command:

```
(.password_game_venv) $ python password_game.py
```

### Configuration

The game expects a configuration file called `config.ini` to be in the current working directory. This file will have a bunch of entries. The entry labeled `[Password Game]` is used to configure the webapp itself:

```
[Password Game]
port = 5000
password_file = passwd
username_file = username
attempts_file = attempts
log_file = main.log
```

The password file is where the current password is stored. The username file is where the current username is stored, and the attempts file logs failed attempts to guess the password right up until someone guesses correctly at which point the attempts file is erased.

The rest of the configuration has sections that look something like this:

```
[SleevelessChampion]
name = Albert T. Nichols
password = football
mother's maiden name = Diaz
date of birth = March 27, 1968
hint = Uses their favorite sport as their password
hobbies = Sports
name of pet = Teddy
favorite color = Red
favorite sports team = Patriots
```

The name of the section is the person's username and the rest are information about the person in question. It is recommended that all properties be filled out. The usernames must be unique in order for the game to function properly.

### Pages

There are 4 pages that are part of this webapp:

+ `/login/` - Displays the actual login prompt as well as the previous attempts to log in.
+ `/view/` - Displays a list of users with links to their personal pages.
+ `/view/<username>/` - Displays the personal page of a given user which shows all their details except their password.
+ `/admin` - This page should be kept secret from the players. It shows a list of users along with their usernames and passwords. Clicking on a password sets that user's username to the username file and password to the password file. This effectively makes that person the target of the hacking game because in order to win, the players must figure out that user's password.
