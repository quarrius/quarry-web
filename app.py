#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import uuid

import flask
import flask_bootstrap
from flask.ext.github import GitHub
from playhouse.flask_utils import FlaskDB, get_object_or_404

from toybox import DB_INIT, User, World

app = flask.Flask(__name__)
app.config.from_pyfile('.context')

flask_bootstrap.Bootstrap(app)
flask_oauth = OAuth(app)

flask_db = FlaskDB(app, DB_INIT(app.config['DATABASE']))

github = GitHub(app)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/login')
def login():
    if flask.session.get('user_guid', None) is None:
        return github.authorize(scope='user:email')
    else:
        return flask.redirect(flask.url_for('index'))

@app.route('/login/callback/github')
@github.authorized_handler
def github_oauth_callback(oauth_token):
    next_url = request.args.get('next') or flask.url_for('index')
    if oauth_token is not None:
        user = User.select().where(User.password == oauth_token).first()
        if user is None:
            user = User.create(username=str(uuid.uuid4()),
                password=oauth_token, email_addr=str(uuid.uuid4()))
        flask.session['user_guid'] = user.guid
        flask.session['github_oauth_token'] = oauth_token
    else:
        # show some kind of error
        pass
    return flask.redirect(next_url)

@app.route('/logout')
def logout():
    flask.session.pop('user_guid', None)
    flask.session.pop('github_oauth_token', None)
    return flask.redirect(flask.url_for('index'))

@github.tokengetter
def get_github_oauth_token():
    user_guid = flask.session.get('user_guid', None)
    github_oauth_token = flask.session.get('github_oauth_token', None)
    if github_oauth_token is None:
        if user_guid is not None:
            user = User.select().where(User.guid == user_guid).get()
            github_oauth_token = user.password
    return github_oauth_token

@app.route('/auth-debug')
def auth_debug():
    if 'user_guid' in flask.session:
        return str(github.get('user'))

@app.route('/m/<string:map_token>')
def view_map(map_token):
    return flask.render_template('view_map.html',
        world=get_object_or_404(
            World.select().where(World.active == True),
            World.map_token == map_token,
    ))

@app.route('/users/<string:user_guid>/worlds')
def list_worlds(user_guid):
    return flask.render_template('users/worlds/list.html',
        user=get_object_or_404(User, User.guid == user_guid),
    )

if __name__ == '__main__':
    if os.environ['TOYBOX_TESTING']:
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
