__author__ = 'geekscruff'

from querybuilder import endpoint, sparql_select
from urllib2 import URLError
import logging

logger = logging.getLogger(__name__)

# TODO a bit more logging and commenting might help here

# Class to perform sparql queries from the search page. There is some hardcoded code in this class to deal with some of
# the quirks of different endpoints.


class SparqlQuery:
    def __init__(self, kind, ep):
        logger.debug("DEBUG sparql_query.py - object instantiated")
        self.kind = kind  # kind of search, so far only 'AND' is supported
        self.ep = ep  # the endpoint
        self.val = ""
        self.ver = ""

    def namesearch(self, value):
        try:
            self.val = value
            if self.kind == "AND":
                if "dbpedia" in self.ep:
                    logger.info("INFO sparql_query.py - querying dbpedia, use multiple UNIONs rather than && shorthand "
                                "for FILTERing")
                    regex = self.buildregextwo()
                # TODO more testing
                # elif "bnb." in self.ep:
                #     regex = self.buildregextwo()
                else:
                    logger.info("INFO sparql_query.py - use the && shorthand for FILTERing")
                    regex = self.buildregexone()
                listy = self.buildtypeandlabel()
                term = ""
                if len(listy) > 1:
                    for i in listy:
                        term += "{ " + i + regex + " } UNION "
                else:
                    for i in listy:
                        term = i + regex

                if term.endswith(' UNION '):
                    term = term[:-7]

                sel = sparql_select.SparqlSelect(term, self.ep, 0, "*")
                sel.distinct()
                logger.debug("DEBUG sparql_query.py - name search performed")
                return sel.select()
        except URLError as e:
            logger.error("URLError sparql_query.py - " + e.message)
            return "error"  # TODO raise exception
        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            return "error"  # TODO raise exception

    # Return all information about a specific subject
    def allsearch(self, value):
        try:
            self.val = value
            term = "{ <" + value + "> ?p ?o }"
            if "dbpedia" in value:
                term = "{ <" + value + "> ?p ?o . FILTER ( isUri(?o) ) }"
                term += ' UNION { <' + value + '> ?p ?o . FILTER ( langMatches(lang(?o),"en" ) ) }'
                term += ' MINUS { <' + value + '> <http://www.w3.org/2002/07/owl#sameAs> ?o . FILTER ( REGEX(?o,"dbpedia.org/resource/") ) }'
            query = sparql_select.SparqlSelect(term, self.ep, 0, "*")
            query.distinct()
            return query.select()
        except URLError as e:
            logger.error("URLError sparql_query.py - " + e.message)
            return "error"  # TODO raise exception
        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            return "error"  # TODO raise exception

    def buildregexone(self):
        #split the value up and create a regex line for each
        if " " in self.val:
            terms = self.val.split()
            regex = " FILTER ("
            for term in terms:
                regex += ' (regex(?o, "' + term + '","i")) && '
        else:
            regex = ' FILTER (regex(?o, "' + self.val + '","i")) '

        if regex.endswith('&& '):
            regex = regex[:-3]
            regex += ")"
        return regex

    # We use this for dbpedia as it chokes on the other version (ie. using && between FILTER statements)
    def buildregextwo(self):
        #split the value up and create a regex line for each
        regex = ""
        if " " in self.val:
            terms = self.val.split()
            for term in terms:
                regex += ' FILTER (regex(?o, "' + term + '","i")) '
        else:
            regex = ' FILTER (regex(?o, "' + self.val + '","i")) '

        return regex

    def buildtypeandlabel(self):
        try:
            results = self.getendpointdetails()
            typelist = []
            typesandlabelslist = []
            label = ""
            for result in results["results"]["bindings"]:
                if result["p"]["value"] == 'http://geekscruff.me/ns/dataset#typeForPersonalName':
                    typelist.append(result["o"]["value"])

                elif result["p"]["value"] == 'http://geekscruff.me/ns/dataset#labelForPersonalName':
                    label = result["o"]["value"]

                elif result["p"]["value"] == 'http://www.w3.org/TR/sparql11-service-description/#sd-supportedLanguage':
                    self.ver = result["o"]["value"]

            for i in typelist:
                typesandlabelslist.append("?s <" + label + "> ?o . ?s a <" + i + "> .")
        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            raise Exception("Something went wrong in building the types and labels")
        return typesandlabelslist

    def getendpointdetails(self):
        return  endpoint.Endpoint(self.ep).setup_existing_sparql_endpoint()