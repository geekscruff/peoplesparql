__author__ = 'geekscruff'

from flask import current_app, Flask
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import datawrangler
import os
import logging

# Global variables
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Creates the connection to the local repository


class Connect():
    def __init__(self, repository):  # Supply the repository name

        # Load the configuration, we need the allegrograph connection information
        if os.path.isfile('/opt/peoplesparql/config.py'):
            logger.info("INFO connect.py - loaded production config")
            app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
        else:
            logger.info("INFO connect.py - loaded local config")
            app.config.from_object('peoplesparql')

        logger.info('INFO connect.py - attempting connection to %s', repository)
        try:
            server = AllegroGraphServer(app.config['AG_HOST'], app.config['AG_PORT'], app.config['AG_USER'], app.config['AG_PASSWORD'])
            self.catalog = server.openCatalog(app.config['AG_CATALOG'])
            self.accessMode = Repository.ACCESS
            self.repo = self.catalog.getRepository(repository, self.accessMode)
            logger.info('INFO connect.py - connected to %s', self.reponame())

        except Exception as e:
            logger.error('ERROR! connect.py - ' + e.message)

    # Returns the repository connection
    def repoconn(self):
        try:
            self.conn = self.repo.getConnection()
            logger.debug('DEBUG connect.py -- return connection')
            return self.conn
        except Exception as e:
            logger.error('ERROR! connect.py - ' + e.message)

    # Returns the repository name
    def reponame(self):
        try:
            return self.repo.getDatabaseName()
        except Exception as e:
            logger.error('ERROR! connect.py - ' + e.message)

    # Returns the full url for the repository
    def repourl(self):
        try:
            return "http://" + app.config['AG_HOST'] + ":" + str(app.config['AG_PORT']) + "/catalogs/" + app.config['AG_CATALOG'] + "/repositories/" + self.reponame()
        except Exception as e:
            logger.error('ERROR! connect.py - ' + e.message)


    # Used for testing, delete all data if the repository name is 'test'
    def deletetestdata(self):
        if self.reponame() == 'test':
            self.repoconn().clear()
            logger.info('INFO connect.py - deleted all statements from %s', self.reponame())

    # Close the repository connection
    def close(self):
        self.repoconn().close();
        self.repo = self.conn.repository
        self.repo.shutDown()
        logger.info('INFO connect.py - connection closed')