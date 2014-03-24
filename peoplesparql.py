import query

__author__ = 'geekscruff'

from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash

#for flaskr
import sqlite3
from contextlib import closing
import datetime

#to check if config file is in place
import os.path

#import blueprints
from project.project import project
from home.home import home
from query.query import query

app = Flask('peoplesparql')

#register blueprints
app.register_blueprint(home)
app.register_blueprint(project)
app.register_blueprint(query)

# Blueprint can be registered many times
app.register_blueprint(home, url_prefix='/')
app.register_blueprint(home, url_prefix='/peoplesparql/')
app.register_blueprint(project, url_prefix='/project')
app.register_blueprint(query, url_prefix='/query')

#local config
TESTING = True
DEBUG = True
SECRET_KEY = 'development key'
DATABASE = '/tmp/peoplesparql.db'
USERNAME = 'admin'
PASSWORD = 'default'

# this is taken from the example code, see doco for generating a new key, need this for sessions
# set the secret key.  keep this really secret
# this is now in the config

if os.path.isfile('/opt/peoplesparql/config.py'):
    #load production config from file
    app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
else:
    #load local config
    app.config.from_object('peoplesparql')

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#for flaskr
@app.route('/blog')
def show_entries():
    cur = g.db.execute('select title, text, created from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], created=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/blog/rss')
def rss():
    return 'I would like an rss feed here'

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    now = str(datetime.datetime.now())
    #date = str(now.day) + "-" + str(now.month) + "-" + str(now.year)

    g.db.execute('insert into entries (title, text, created) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], now[:16]])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['user'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/config')
def config():
    return "TESTING " + str(app.config['TESTING']) + "<br />DEBUG " + str(app.config['DEBUG'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#for flaskr
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
    init_db()
    app.run()
