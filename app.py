#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import flask
import flask_bootstrap
from playhouse.flask_utils import FlaskDB, get_object_or_404

from toybox import DB_OBJ, User, World, db_config

app = flask.Flask(__name__)
app.config.from_pyfile('.context')

flask_bootstrap.Bootstrap(app)

DB_NAME, DB_CONFIG = db_config(app.config['DATABASE'])
DB_OBJ.init(DB_NAME, **DB_CONFIG)
flask_db = FlaskDB(app, DB_OBJ)


@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')

@app.route('/m/<string:map_token>')
def view_map(map_token):
    return flask.render_template('view_map.html',
        world=get_object_or_404(
            World.select().where(World.active == True),
            World.map_token == map_token,
    ))

if __name__ == '__main__':
    try:
        DB_OBJ.create_tables([User, World])
    except Exception:
        pass
    app.run()
