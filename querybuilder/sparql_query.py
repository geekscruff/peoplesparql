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
                # issue with dbpedia querying seems to have gone away!
                # if "dbpedia" in self.ep:
                #     logger.info("INFO sparql_query.py - querying dbpedia, use multiple UNIONs rather than && shorthand "
                #                 "for FILTERing")
                #     regex = self.buildregextwo()
                #else:
                logger.info("INFO sparql_query.py - use the && shorthand for FILTERing")
                regex = self.buildregexone()
                listy = self.buildtypeandlabel()
                term = ""
                lang = ''
                if "dbpedia" in self.ep or "freebase" in self.ep or "yago" in self.ep:
                    lang = ' FILTER (langMatches(lang(?o),"en" ))'
                if len(listy) > 1:
                    for i in listy:
                        term += "{ " + i + regex + lang + " } UNION "
                else:
                    for i in listy:
                        term = i + regex + lang

                if term.endswith(' UNION '):
                    term = term[:-7]
                sel = sparql_select.SparqlSelect(term, self.ep, sel="?s ?o", dist=True, order="?o")
                logger.debug("DEBUG sparql_query.py - name search performed")
                return sel.select()
        except URLError as e:
            logger.error("URLError sparql_query.py - " + e.message)
            return "error"  # TODO raise exception
        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            return "error"  # TODO raise exception

    # Return all information about a specific subject
    # aTODO build in support for isLiteral and isURI here
    def allsearch(self, value, type):
        try:
            self.val = value
            term = "{ <" + value + "> ?p ?o "
            if type == "uri":
                term += ". FILTER (isURI(?o)) }"
                # This might not be ideal, what this is trying to do is remove refs to different
                # language versions of the same resource
                if "dbpedia" in value or "freebase" in value or "yago" in value:
                    term += ' MINUS { <' + value + '> <http://www.w3.org/2002/07/owl#sameAs> ?o . ' \
                        'FILTER ( REGEX(?o,"dbpedia.org/resource/") ) }'
            elif type == "literal":
                # we don't get numbers (eg. dates) if we include this
                #if "dbpedia" in value or "freebase" in value or "yago" in value:
                #    term += '. FILTER (isLiteral(?o)) FILTER (langMatches(lang(?o),"en" )) }'
                #else:
                term += ". FILTER (isLiteral(?o)) }"
            else:
                term += " }"
            # limit number, British Museum in particular can have thousands of triples (one found with 86000!)
            query = sparql_select.SparqlSelect(term, self.ep, sel="*", dist=True, limit='500')
            return query.select()
        except URLError as e:
            logger.error("URLError sparql_query.py - " + e.message)
            return "error"  # TODO raise exception
        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            return "error"  # TODO raise exception

    def buildregexone(self):
        #split the value up and create a regex line for each
        if " " in self.val or "." in self.val:
            # replace any dots with spaces and any double spaces with single
            value = self.val.replace(".", " ").replace("  ", " ")
            terms = value.split()
            regex = " FILTER ("
            for term in terms:
                # if term is only one character it is likely to be an initial
                # let's look for it at the start of the label or preceeded with a space
                if len(term) == 1:
                    regex += ' (regex(?o, " ' + term + '","i") || regex(?o, "^' + term + '","i")) && '
                # if term is two characters, let's look for each letter as though they are initials
                # and for the term itself, as the start of a name
                elif len(term) == 2:
                    regex += ' (regex(?o, " ' + term + '","i") || regex(?o, "^' + term + '","i") || ' \
                        '((regex(?o, " ' + term[0] + '","i") || regex(?o, "^' + term[0] + '","i")) && ' \
                        '(regex(?o, " ' + term[1] + '","i") || regex(?o, "^' + term[1] + '","i")))) && '
                else:
                    regex += ' (regex(?o, "' + term + '","i")) && '
        else:
            regex = ' FILTER (regex(?o, "' + self.val + '","i")) '

        if regex.endswith('&& '):
            regex = regex[:-3]
            regex += ")"
        return regex

    # We use this for dbpedia as it chokes on the other version (ie. using && between FILTER statements)
    # 14/7/2014 this problem seems to have disappeared
    # def buildregextwo(self):
    #     #split the value up and create a regex line for each
    #     regex = ""
    #     if " " in self.val or "." in self.val:
    #         value = self.val.replace(".", " ").replace("  ", " ")
    #         terms = value.split()
    #         for term in terms:
    #             if len(term) == 1:
    #                 regex += ' FILTER (regex(?o, " ' + term + '","i") || regex(?o, "^' + term + '","i")) '
    #             elif len(term) == 2:
    #                 regex += ' FILTER (regex(?o, " ' + term + '","i") || regex(?o, "^' + term + '","i")) '
    #                 #for now we just search for both letters together, but ideally would break up and search individually too
    #                 #this is not easy for DBpedia which does not seem happy with the && shorthand
    #                 #regex += ' FILTER (regex(?o, " ' + term[0] + '","i") || regex(?o, "^' + term[0] + '","i"))'
    #                 #regex += ' FILTER (regex(?o, " ' + term[:1] + '","i") || regex(?o, "^' + term[:1] + '","i"))'
    #             else:
    #                 regex += ' FILTER (regex(?o, "' + term + '","i")) '
    #
    #     else:
    #         regex = ' FILTER (regex(?o, "' + self.val + '","i")) '
    #
    #     regex += ' FILTER ( langMatches(lang(?o),"en" )) '
    #
    #     return regex

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

            if len(typelist) == 0:
                for result in results["results"]["bindings"]:
                    if result["p"]["value"] == 'http://geekscruff.me/ns/dataset#labelForPersonalName':
                        typesandlabelslist.append("?s <" + result["o"]["value"] + "> ?o .")

        except Exception as e:
            logger.error("ERROR! sparql_query.py - " + e.message)
            raise Exception("Something went wrong in building the types and labels")
        return typesandlabelslist

    def getendpointdetails(self):
        return  endpoint.Endpoint(self.ep).setup_existing_sparql_endpoint()