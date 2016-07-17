#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import flask
import flask_bootstrap

app = flask.Flask(__name__)
flask_bootstrap.Bootstrap(app)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')

@app.route('/m/<string:map_id>')
def view_map(map_id):
    return flask.render_template('view_map.html',
        map_id=map_id,
    )

if __name__ == '__main__':
    app.run()
