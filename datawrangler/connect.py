__author__ = 'geekscruff'

"""Creates the connection to the local repository"""

from flask import Flask
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import os
import logging

# Global variables
logger = logging.getLogger(__name__)
app = Flask(__name__)

class Connect():
    def __init__(self, repository, cat='default', new=False):  # Supply the repository name

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
            # public_catalog is default; supply a catalog value to use a different catalogue
            if cat == 'default':
                self.catalog = server.openCatalog(app.config['AG_CATALOG'])
            else:
                self.catalog = server.openCatalog(cat)
            self.accessMode = Repository.ACCESS
            # default is to use an existing repository
            if not new:
                self.repo = self.catalog.getRepository(repository, self.accessMode)
            # if new is true, create a new repository (if it already exists, request is ignored and existing repo used)
            else:
                self.repo = self.catalog.createRepository(repository)
                self.repo = self.catalog.getRepository(repository, self.accessMode)

            logger.info('INFO connect.py - connected to %s', self.reponame())

        except Exception as e:
            logger.error('ERROR! connect.py 1 - ' + e.message)

    # Returns the repository connection
    def repoconn(self):
        try:
            self.conn = self.repo.getConnection()
            logger.debug('DEBUG connect.py -- return connection')
            return self.conn
        except Exception as e:
            logger.error('ERROR! connect.py 2 - ' + e.message)

    # Returns the repository name
    def reponame(self):
        try:
            return self.repo.getDatabaseName()
        except Exception as e:
            logger.error('ERROR! connect.py 3 - ' + e.message)

    # Returns the full url for the repository
    def repourl(self):
        try:
            return "http://" + app.config['AG_HOST'] + ":" + str(app.config['AG_PORT']) + "/catalogs/" + self.catalog.getName() + "/repositories/" + self.reponame()
        except Exception as e:
            logger.error('ERROR! connect.py 4 - ' + e.message)


    # Used for testing, delete all data if the repository name is 'test'
    def deletetestdata(self):
        if self.reponame() == 'test':
            self.repoconn().clear()
            logger.info('INFO connect.py - deleted all statements from %s', self.reponame())

    # Close the repository connection
    def close(self):
        logger.info('INFO connect.py - connection closed')
        self.repoconn().close();
        self.repo = self.conn.repository
        self.repo.shutDown()