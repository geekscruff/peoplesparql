__author__ = 'geekscruff'

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions, XML
from simplejson import JSONDecodeError
from urllib2 import HTTPError
import logging

logger = logging.getLogger(__name__)

# Perform a SELECT query on the specified endpoint, with the specified value


class SparqlSelect():
    def __init__(self, value, ep, limit=0, sel='*', dist=False, order='', group='', ng=''):
        logger.debug("SparqlSelect object instantiated")
        self.value = value  # query value
        self.ep = ep  # the endpoint
        self.limit = limit  # default is 0 to add no limit for results returned
        self.sel = sel  # any combination of ?s (subject) ?p (predicate) and ?o (object), or * for all
        self.dist = dist  # Use true to limit the query to distinct
        self.order = order  # default is no ordering
        self.group = group  # default is no grouping
        self.ng = ng  # default graph

        self.pref = ''

    # Add a set of prefixes so that shorthand can be used in query itself
    def addprefixes(self, prefixes):

        # If this method is called, add these as a default if the supplied value is blank
        if prefixes == "default":
            prefixes = "PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX dcterms: <http://purl.org/dc/terms/> " \
                       "PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                       "PREFIX rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:	<http://www.w3.org/2000/01/rdf-schema#> " \
                       "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX crm: <http://erlangen-crm.org/current/>"
        self.pref = prefixes


    def select(self):
        try:
            query_string = ""
            sparqlquery = SPARQLWrapper(self.ep)

            if self.pref:
                query_string = self.pref

            query_string += "SELECT "

            if self.dist:
                query_string += "DISTINCT "

            query_string += self.sel

            if self.ng:
                query_string += " FROM " + self.ng

            query_string += " WHERE { " + self.value + " }"

            if self.limit is not 0:
                query_string = query_string + " LIMIT " + str(self.limit)

            if self.order:
                query_string = query_string + " ORDER BY " + str(self.order)

            if self.group:
                query_string = query_string + " GROUP BY " + str(self.group)

            logger.info("INFO sparql_select.py - query string: " + query_string)
            #print(query_string)  # can be useful for debugging

            sparqlquery.setQuery(query_string)
            sparqlquery.setReturnFormat(JSON)
            results = sparqlquery.query().convert()

            return results

        except SPARQLExceptions.QueryBadFormed as e:
            logger.error("ERROR! QueryBadFormed sparql_select.py - " + e.message)
            return "error"  # TODO raise an exception
        except SPARQLExceptions.EndPointInternalError as e:
            logger.error("ERROR! EndPointInternalError sparql_select.py - " + e.message)
            return "error"  # TODO raise an exception
        except JSONDecodeError as e:
            logger.error("JSONDecodeError sparql_select.py - " + e.message + " (get results as XML instead)")
            sparqlquery.setReturnFormat(XML)
            results = sparqlquery.query().convert()
            xml = results.toxml()
            return xml
        except HTTPError as e:
            logger.error("HTTPError sparql_select.py - HTTP error code: " + str(e.code))
            return "error"  # TODO raise an error here instead
        except Exception as e:  # for anything else
            logger.error("ERROR! sparql_select.py - " + e.message)
            return "error"  # TODO raise an error here instead