__author__ = 'geekscruff'


"""Perform an ASK query on the specified endpoint, with the specified value"""

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions, XML
from simplejson import JSONDecodeError
from urllib2 import HTTPError
import logging

logger = logging.getLogger(__name__)


class SparqlAsk():
    def __init__(self, value, ep):
        logger.debug("DEBUG sparql_ask.py - object instantiated")
        self.value = value  # the query value
        self.ep = ep  # the endpoint

    def ask(self):
        try:
            sparqlquery = SPARQLWrapper(self.ep)
            query_string = "ASK { " + self.value + " }"
            logger.info("INFO sparql_ask.py - query string: " + query_string)
            sparqlquery.setQuery(query_string)
            sparqlquery.setReturnFormat(JSON)
            results = sparqlquery.query().convert()
            return results
        except SPARQLExceptions.QueryBadFormed as e:
            logger.error("SPARQLExceptions.QueryBadFormed sparql_ask.py - " + e.message)
            return "error"
        except JSONDecodeError as e:  #some endpoints (eg. British Museum) don't return json for an ask request, so here we get XML data
            logger.error("JSONDecodeError sparql_ask.py - " + e.message + " (get results as XML instead)")
            sparqlquery.setReturnFormat(XML)
            results = sparqlquery.query().convert()
            xml = results.toxml()
            return xml
        except HTTPError as e:
            logger.error("HTTPError sparql_ask.py - HTTP error code: " + str(e.code))
            return "error"  # TODO raise an error here instead
        except Exception as e:
            logger.error("ERROR! sparql_ask.py - " + e.message)
            return "error"  # TODO raise an error here instead
