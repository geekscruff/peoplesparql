__author__ = 'geekscruff'

from datawrangler import connect, addtriple
from querybuilder import sparql_ask, sparql_select
import logging
import warnings

logger = logging.getLogger(__name__)
warnings.simplefilter('error', RuntimeWarning) # filter any runtime warnings and throw an exception

# TODO private methods http://legacy.python.org/dev/peps/pep-0008/#comments


def switch(x):  # Simple switch method to allow looping through the different Person types
    return {
        1: 'http://xmlns.com/foaf/0.1/Person',
        2: 'http://dbpedia.org/ontology/Person',
        3: 'http://erlangen-crm.org/current/E21_Person',
        4: 'http://purl.org/dc/elements/1.1/creator',
        5: 'http://purl.org/dc/terms/creator',
        6: 'http://purl.org/ontology/mo/MusicArtist',
        7: 'http://rdf.freebase.com/ns/base.litcentral.named_person',
        8: 'http://rdf.freebase.com/ns/people.person',
        9: 'http://schema.org/Person',
        10: 'http://www.ontotext.com/proton/protontop#Person',
        11: 'http://www.w3.org/2002/07/owl#NamedIndividual',
    }.get(x, 1)  # 1 is default if x not found

# Class to handle the creation of an endpoint. First checks the local datastores repository to see if we already have
# the endpoint setup and, if we don't, queries the endpoint to find out the information we want.



class EndpointCreator:
    def __init__(self, ep, repo):
        logger.debug("DEBUG endpoint_creator.py - object instantiated")
        self.sparql = ep
        self.repo = repo
        self.name = ep
        self.conn = ""

    # Supply a specific name for the endpoint. Used only where we believe this is a new endpoint.
    def setname(self, name):
        self.name = name

    def docreate(self):
        # First check if we already have the specified endpoint
        exists = str.lower(str(self.askforlocalendpoint()))

        if "false" in exists:  #setup new endpoint and store data
            logger.info("INFO endpoint_creator.py - endpoint is not in local repository, let's set it up")
            self.conn = connect.Connect(self.repo).repoconn()
            try:
                self.setupendpoint()
                self.conn.deleteDuplicates('spo') #clean up the repository to remove any duplicate values
                self.conn.close
                return self.selectforlocalendpoint()
            except Exception as e:
                logger.error("ERROR! endpoint_creator.py - " + e.message)
                raise Exception(e.message)

        elif "true" in exists:
            logger.info("INFO endpoint_creator.py - endpoint is in local repository, returning information")
            return self.selectforlocalendpoint()
        else:
            raise Exception("Something went wrong")

    # Ask query to check if endpoint exists in local datastores repo
    def askforlocalendpoint(self):
        return sparql_ask.SparqlAsk("?s <http://www.w3.org/TR/sparql11-service-description/#sd-endpoint> <" + self.sparql + ">", connect.Connect(self.repo).repourl()).ask()

    # Select query to get info on the endpoint from the local datastores repo
    def selectforlocalendpoint(self):
        return sparql_select.SparqlSelect("{ <http://geekscruff/ns/datasetservicedby#" + self.sparql + "> ?p ?o } UNION { <" + self.sparql + "> ?p ?o}", connect.Connect(self.repo).repourl(), 0, "?p ?o").select()

    # Discover and store information about the sparql endpoint
    def setupendpoint(self):
            try:
                results = sparql_ask.SparqlAsk("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(1) + ">", self.sparql).ask()
                add = addtriple.AddTriple(self.conn)
                add.setupsubject(self.sparql)
                # If the SPARQL ASK query fails, this suggests SPARQL 1.1 is not supported
                if results == "error":
                    logger.debug("DEBUG endpoint_creator.py - ASK query returned an error,"
                                 " assume the endpoint supports SPARQL 1.0 only")
                    self.setupdataset(10) # only if this succeeds do we continue with the endpoint info
                    add.adduri('http://www.w3.org/TR/sparql11-service-description/#sd-supportedLanguage',
                               'http://www.w3.org/TR/sparql11-service-description/#SPARQL10Query')
                else:
                    logger.debug("DEBUG endpoint_creator.py - ASK query succeeded,"
                                 " assume the endpoint supports SPARQL 1.1")
                    self.setupdataset(11) # only if this succeeds do we continue with the endpoint info
                    add.adduri('http://www.w3.org/TR/sparql11-service-description/#sd-supportedLanguage',
                               'http://www.w3.org/TR/sparql11-service-description/#SPARQL11Query')

                add.addrdftype('http://www.w3.org/TR/sparql11-service-description/#sd-Service')
                add.adduri('http://www.w3.org/TR/sparql11-service-description/#sd-endpoint', self.sparql)
                add.addliteral('http://dublincore.org/documents/dcmi-terms/#elements-title', self.name)

            except RuntimeWarning as e:  # This is raised if the endpoint is not a valid sparql endpoint
                raise Exception(e.message)

    # Discover and store information about the dataset
    def setupdataset(self, version):
        add = addtriple.AddTriple(self.conn)
        add.setupsubject('http://geekscruff/ns/datasetservicedby#' + self.sparql)

        # If the original ASK query fails, use SELECT queries
        if version == 10:
            logger.debug("DEBUG endpoint_creator.py - check what rdf:type value is used for Persons "
                         "and what rdfs:label is used; add both to local repository")

            # Loop through our internal list of eleven personal name types
            for x in xrange(11):
                res = sparql_select.SparqlSelect("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + ">", self.sparql, 1, "*").select()
                if "[]" not in str(res):
                    add.adduri('http://rdfs.org/ns/void#sparqlEndpoint', self.sparql)
                    add.adduri('http://geekscruff.me/ns/dataset#typeForPersonalName', switch(x + 1))

                    # Check for rdfs:label and skos:prefLabel - assuming that one or other of these will be used, if not setup will fail
                    label1 = sparql_select.SparqlSelect("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + "> . ?s http://www.w3.org/2000/01/rdf-schema#label ?o", self.sparql, 1, "?s").select()
                    if "[]" not in str(label1):
                        add.adduri('http://geekscruff.me/ns/dataset#labelForPersonalName', 'http://www.w3.org/2000/01/rdf-schema#label')
                    label2 = sparql_select.SparqlSelect("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + "> . ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?o", self.sparql, 1, "?s").select()
                    if "[]" not in str(label2):
                        add.adduri('http://geekscruff.me/ns/dataset#labelForPersonalName', 'http://www.w3.org/2004/02/skos/core#prefLabel')

        # If the original ASK query succeeds, use ASK queries
        elif version == 11:
            logger.debug("DEBUG endpoint_creator.py - check what rdf:type value is used for Persons "
                         "and what rdfs:label is used; add both to local repository")

            # Loop through our internal list of eleven personal name types
            for x in xrange(11):
                res = sparql_ask.SparqlAsk("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + ">", self.sparql).ask()
                if "true" in str.lower(str(res)):
                    add.adduri('http://geekscruff.me/ns/dataset#typeForPersonalName', switch(x + 1))

                    # Check for rdfs:label and skos:prefLabel - assuming that one or other of these will be used, if not setup will fail
                    label1 = sparql_ask.SparqlAsk("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + "> . ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o", self.sparql).ask()
                    if "true" in str.lower(str(label1)):
                        add.adduri('http://geekscruff.me/ns/dataset#labelForPersonalName', 'http://www.w3.org/2000/01/rdf-schema#label')
                    label2 = sparql_ask.SparqlAsk("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + switch(x + 1) + "> . ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?o", self.sparql).ask()
                    if "true" in str.lower(str(label2)):
                        add.adduri('http://geekscruff.me/ns/dataset#labelForPersonalName', 'http://www.w3.org/2004/02/skos/core#prefLabel')