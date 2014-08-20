__author__ = 'geekscruff'

#Production configuration settings

DEBUG = False  # change to true for testing
TESTING = False  # change to true for testing
SECRET_KEY = 'changeme'
USERNAME = 'changeme'
PASSWORD = 'changeme'
LOGLEVEL = 'ERROR'  # ERROR is recommended for production
PERSONA_JS = 'https://login.persona.org/include.js'
PERSONA_VERIFIER = 'https://verifier.login.persona.org/verify'

# Configuration settings for working with Allegrograph graph db, see http://franz.com/agraph/allegrograph/
AG_DATASOURCES = 'changeme'  # repository name
AG_HOST = 'localhost'  # likely to be server name
AG_PORT = 10035  # assuming standard installation
AG_CATALOG = 'public-catalog'  # this needs to exist in local allegrograph
AG_USER = 'changeme'  # this needs to exist as use in local allegrograph with read/write access to the datasources repository
AG_PASSWORD = 'changeme'  # this needs to be the right password in local allegrograph
GOOGLE_API_KEY = 'changeme'  #currently unused, would be used for querying freebase
