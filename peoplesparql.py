__author__ = 'geekscruff'

"""This is the main class for the peoplesparql application."""

from flask import Flask, request, session, g, abort, json, render_template
from home.home import home
from project.project import project
from research.research import research
import requests
import logging
import os.path

from simplekv.memory import DictStore

# This is currently made available locally as I was not able to get this working via environment
from flaskext.kvsession import KVSessionExtension

"""a DictStore will store everything in memory; other stores may be more useful,
like the FilesystemStore, see the simplekv documentation for details"""
store = DictStore()

logger = logging.getLogger(__name__)

# Get the app for use in setting up the config
app = Flask(__name__)

# Replace the app's session handling
# Used because some of the sessions are larger than can be stored in the client browser
KVSessionExtension(store, app)

# Register the blueprints
app.register_blueprint(home)
app.register_blueprint(project)
app.register_blueprint(research)

# Register the urls for the blueprints
app.register_blueprint(home, url_prefix='/')
app.register_blueprint(home, url_prefix='/peoplesparql/')

app.register_blueprint(project, url_prefix='/project')
app.register_blueprint(project, url_prefix='/info')

app.register_blueprint(research, url_prefix='/query')
app.register_blueprint(research, url_prefix='/explore')
app.register_blueprint(research, url_prefix='/create')

# Use this local config if the production config is not available
TESTING = True
DEBUG = True
SECRET_KEY = 'development key'
PERSONA_JS = 'https://login.persona.org/include.js'
PERSONA_VERIFIER = 'https://verifier.login.persona.org/verify'
LOGLEVEL = 'DEBUG'
# Configuration settings for working with Allegrograph graph db, see http://franz.com/agraph/allegrograph/
AG_DATASOURCES = 'test'
AG_HOST = 'localhost' # this needs to exist in local allegrograph
AG_PORT = 10035 # assuming standard installation
AG_CATALOG = 'public-catalog' # this needs to exist in local allegrograph
AG_USER = 'test' # this needs to exist as use in local allegrograph with read/write access to 'test'
AG_PASSWORD = '1234' # this needs to be the right password in local allegrograph
GOOGLE_API_KEY = 'changeme' # not currently used

# Check for the production config file and load. If it is missing load the configuration from the current object.
if os.path.isfile('/opt/peoplesparql/config.py'):
    app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
else:
    app.config.from_object('peoplesparql')

if app.config['LOGLEVEL'] == 'INFO':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename='/opt/peoplesparql/peoplesparql.log')
    logging.basicConfig()
elif app.config['LOGLEVEL'] == 'DEBUG':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename='/opt/peoplesparql/peoplesparql.log')
else:
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/opt/peoplesparql/peoplesparql.log')

logger.info('INFO peoplesparql.py - logging Level ' + app.config['LOGLEVEL'])


# This is used to test if the app is in test or production mode
@app.route('/config')
def config():
    return "TESTING " + str(app.config['TESTING']) + "<br />DEBUG " + str(app.config['DEBUG'])


# User login provided by the Flask persona example: https://github.com/mitsuhiko/flask/tree/master/examples/persona
@app.before_request
def get_current_user():
    g.user = None
    email = session.get('email')
    if email is not None:
        g.user = email


@app.route('/_auth/login', methods=['GET', 'POST'])
def login_handler():
    """This is used by the persona.js file to kick off the
    verification securely from the server side.  If all is okay
    the email address is remembered on the server.
    """
    resp = requests.post(app.config['PERSONA_VERIFIER'], data={
        'assertion': request.form['assertion'],
        'audience': request.host_url,
    }, verify=True)
    if resp.ok:
        verification_data = json.loads(resp.content)
        if verification_data['status'] == 'okay':
            session['email'] = verification_data['email']
            return 'OK'

    abort(400)


@app.route('/_auth/logout', methods=['POST'])
def logout_handler():
    """This is what persona.js will call to sign the user
    out again.
    """
    session.clear()
    return 'OK'

# Handle HTTP 400 errors by directing to a custom error page
@app.errorhandler(500)
def error(e):
    return render_template('500.html'), 500

# And finally, run!
if __name__ == '__main__':
    app.run()
