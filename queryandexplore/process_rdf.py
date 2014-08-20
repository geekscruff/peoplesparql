__author__ = 'geekscruff'

"""Sits between the interface and the rdflib classes """


from flask import Flask
from rdflib.graph import ConjunctiveGraph, Graph
import urllib
from urllib2 import URLError
from xml.sax import SAXParseException
import logging
import os

# Global variables
logger = logging.getLogger(__name__)
app = Flask(__name__)

class ProcessRdf():
    def __init__(self):
        logger.info("INFO process_rdf.py - object instantiated")
        self.uri = ''

        # Load the configuration, we need the allegrograph connection information
        if os.path.isfile('/opt/peoplesparql/config.py'):
            logger.info("INFO process_rdf.py - loaded production config")
            app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
        else:
            logger.info("INFO process_rdf.py - loaded local config")
            app.config.from_object('peoplesparql')

    def fromuri(self, uri):

        self.uri = uri

        if not uri.startswith('http://rdf.freebase.com'):
            self.checkuri()
            try:
                g = ConjunctiveGraph()
                g.load(self.uri)

                if g:
                    logger.info("INFO process_rdf.py - returning graph for " + self.uri)
                    return g

                else:
                    raise Exception('Nothing was returned, probably caused URL serving no RDF or bad RDF (eg. Freebase): '
                                    '"No handlers could be found for logger "process_rdf.py" -- uri was ' + self.uri)

            except URLError as e:
                logger.error("URLError process_rdf.py - " + e.message)
                raise Exception('URLError, cause either bad URL or no internet connection - ' + e.message + '(uri was ' + self.uri + ')')
            except SAXParseException as e:
                logger.error("SAXParseException process_rdf.py - " + e.message + '(uri was' + self.uri + ')')
                raise Exception('SAXParseException')
            except AttributeError as e:
                logger.error("AttributeError process_rdf.py - " + e.message + '(uri was' + self.uri + ')')
                raise Exception('AttributeError')
        else:
            self.fromfreebaseuri()

    def checkuri(self):

        # Append /rdf to end of VIAF uris
        if self.uri.startswith('http://viaf'):
            if not self.uri.endswith('/rdf'):
                if not self.uri.endswith('/'):
                    self.uri += '/rdf'
                else:
                    self.uri += 'rdf'

    # just a test
    def fromuri2(self, uri):

        self.uri = uri

        if not uri.startswith('http://rdf.freebase.com'):
            self.checkuri()
            try:
                g = Graph()
                g.parse(self.uri)

                if g:
                    logger.info("INFO process_rdf.py - returning graph for " + self.uri)
                    return g

                else:
                    raise Exception('Nothing was returned, probably caused URL serving no RDF or bad RDF (eg. Freebase): '
                                    '"No handlers could be found for logger "process_rdf.py" -- uri was ' + self.uri)

            except URLError as e:
                logger.error("URLError process_rdf.py - " + e.message)
                raise Exception('URLError, cause either bad URL or no internet connection - ' + e.message + '(uri was ' + self.uri + ')')
            except SAXParseException as e:
                logger.error("SAXParseException process_rdf.py - " + e.message + '(uri was' + self.uri + ')')
                raise Exception('SAXParseException')
            except AttributeError as e:
                logger.error("AttributeError process_rdf.py - " + e.message + '(uri was' + self.uri + ')')
                raise Exception('AttributeError')
        else:
            self.fromfreebaseuri()

    # this doesn't do anything at the moment
    def fromfreebaseuri(self):
        logger.error("ERROR process_rdf.py - freebase uris are not currently supported - " + self.uri)

        # freebase api doco https://developers.google.com/freebase/v1/getting-started#api-keys
        # need to register a google public api key
        #
        # api_key = app.config['GOOGLE_API_KEY']
        # service_url = 'https://www.googleapis.com/freebase/v1/rdf'
        #
        # if self.uri.startswith('http://rdf.freebase.com/ns/m.'):
        #     parts = self.uri.split('/m.')
        #     topic_id = 'm/' + parts[1]
        # elif self.uri.startswith('http://rdf.freebase.com/ns/m/'):
        #     parts = self.uri.split('/m/')
        #     topic_id = 'm/' + parts[1]
        #
        # params = {
        #     'key': api_key
        # }
        # url = service_url + topic_id + '?' + urllib.urlencode(params)
        #
        # # this will fail due to freebase data containing full stops
        # # solution would be to read it in and re-process
        # g = ConjunctiveGraph()
        # g.load(url)


