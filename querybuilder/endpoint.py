__author__ = 'geekscruff'

from flask import Flask
import endpoint_creator
import os
import logging

# Global variables
logger = logging.getLogger(__name__)
app = Flask(__name__)

#This class is used to create endpoints of different types. Currently only sparql is supported.


class Endpoint:
    def __init__(self, ep):
        logger.debug("DEBUG endpoint.py - object instantiated")
        self.ep = ep
        self.details = ""

        if os.path.isfile('/opt/peoplesparql/config.py'):
            logger.info("INFO endpoint.py - loaded production config")
            app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
        else:
            logger.info("INFO endpoint.py - loaded local config")
            app.config.from_object('peoplesparql')

    # Used for new endpoints, although if the endpoint does exist in the repository, that's fine.
    def setup_new_sparql_endpoint(self, name):
        try:
            ep = endpoint_creator.EndpointCreator(self.ep, app.config['AG_DATASOURCES'])
            ep.setname(name)
            results = ep.docreate()
            logger.debug("DEBUG endpoint.py - results from endpoint created returned")
            return results
        except ValueError as e:
            logger.error("ValueError endpoint.py -  " + e.message)
            raise ValueError(e.message)
        except Exception as e:
            logger.error("ERROR! endpoint.py -  " + e.message)
            raise Exception(e.message)

    # Used for endpoints we believe are already in the repository, although if they aren't, that's fine.
    def setup_existing_sparql_endpoint(self):
        try:
            results = endpoint_creator.EndpointCreator(self.ep, app.config['AG_DATASOURCES']).docreate()
            logger.debug("DEBUG endpoint.py - results from endpoint created returned")
            return results
        except ValueError as e:
            logger.error("ValueError endpoint.py --  " + e.message)
            raise ValueError(e.message)
        except Exception as e:
            logger.error("ERROR! endpoint.py -- " + e.message)
            raise Exception(e.message)

    def setup_opensearch_endpoint(self):
        return "TODO"

    def setdetails(self, d):
        logger.debug("DEBUG endpoint.py - store the JSON results")
        self.details = d

    def getdetails(self):
        logger.debug("DEBUG endpoint.py - return the endpoint details as JSON results")
        return self.details

    # Not yet implemented (may not be needed)
    def geturi(self):
        #parse the json and get the uri
        return "uri"

