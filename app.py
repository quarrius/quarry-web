#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import uuid
import hashlib

import flask
import flask_bootstrap
from flask_github import GitHub
from playhouse.flask_utils import FlaskDB, get_object_or_404

from toybox.config import CFG
from toybox.models import User, World
from toybox.db import DATABASE

app = flask.Flask(__name__)
app.config['GITHUB_CLIENT_ID'] = CFG.get('config:quarry-web:GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = CFG.get('config:quarry-web:GITHUB_CLIENT_SECRET')
app.config['SECRET_KEY'] = CFG.get('config:quarry-web:SECRET_KEY')

flask_bootstrap.Bootstrap(app)
github = GitHub(app)
flask_db = FlaskDB(app, DATABASE)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/login')
def login():
    if flask.session.get('user_guid', None) is None:
        github_oauth_token = flask.session.get('github_oauth_token', None)
        if github_oauth_token is None:
            return github.authorize(scope='user:email')
        user = User.select().where(User.password == github_oauth_token)
        flask.session['user_guid'] = user.guid
    return flask.redirect(flask.url_for('index'))

@app.route('/login/callback/github')
@github.authorized_handler
def github_oauth_callback(github_oauth_token):
    next_url = flask.request.args.get('next') or flask.url_for('index')
    if github_oauth_token is not None:
        flask.session['github_oauth_token'] = github_oauth_token
        gh_user = github.get('user')
        if gh_user['email'] is None:
            gh_user['email'] = hashlib.sha256(gh_user['login']).hexdigest()
        app.logger.debug('Fetched Github user data: %r', gh_user)
        user = User.select().where(User.username == gh_user['login']).first()
        if user is None:
            user = User.create(
                username=gh_user['login'],
                password=github_oauth_token,
                email_addr=gh_user['email'],
            )
        else:
            user.password = github_oauth_token
            user.save()
        user.xattr['gh_user'] = {k: v for k, v in gh_user.iteritems() if v != ''}
        flask.session['user_guid'] = user.guid
    else:
        # show some kind of error
        pass
    return flask.redirect(next_url)

@app.route('/logout')
def logout():
    flask.session.pop('user_guid', None)
    flask.session.pop('github_oauth_token', None)
    return flask.redirect(flask.url_for('index'))

@github.access_token_getter
def get_github_oauth_token():
    user_guid = flask.session.get('user_guid', None)
    github_oauth_token = flask.session.get('github_oauth_token', None)
    if github_oauth_token is None:
        if user_guid is not None:
            user = User.select().where(User.guid == user_guid).get()
            github_oauth_token = user.password
    return github_oauth_token

@app.route('/m/<string:map_token>')
def view_map(map_token):
    return flask.render_template('view_map.html',
        world=get_object_or_404(
            World.select().where(World.active == True),
            World.map_token == map_token,
    ))

@app.route('/worlds')
def list_worlds():
    return flask.render_template('users/worlds/list.html',
        user=get_object_or_404(User, User.guid == flask.session.get('user_guid', None)),
    )

if __name__ == '__main__':
    if os.environ.get('TOYBOX_TESTING'):
        try:
            flask_db.database.create_tables([User, World])
        except Exception as err:
            pass
        try:
            u = User.create(user_name='testuser', password='12345', email_addr='u@d')
            wlds = [World.create(user=u, name='world-%d' % i) for i in range(3)]

            print u.guid
            print [w.guid for w in wlds]
        except Exception as err:
            pass

    app.run()
