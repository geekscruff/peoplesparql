__author__ = 'geekscruff'

import os

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.rdfs import RDFS
from querybuilder import sparqlquery


AG_HOST = os.environ.get('AGRAPH_HOST', 'geekscruff.me')
AG_PORT = int(os.environ.get('AGRAPH_PORT', '10035'))
AG_CATALOG = os.environ.get('AGRAPH_CATALOG', 'public-catalog')
# AG_CATALOG = ''
AG_REPOSITORY = 'test'
AG_USER = 'test'
AG_PASSWORD = 'xyzzy'

class Add:
    def __init__(self):
        server = AllegroGraphServer(AG_HOST, AG_PORT, AG_USER, AG_PASSWORD)
        catalog = server.openCatalog(AG_CATALOG)
        accessMode=Repository.ACCESS
        self.repo = catalog.getRepository(AG_REPOSITORY, accessMode)
        self.conn = self.repo.getConnection()
        self.query_string = ""

    def update(self, value):
        ## create some resources and literals to make statements out of
        self.value = value
        noblanksvalue = value.replace(" ", "")
        subject = self.conn.createURI("http://geekscruff.me/people/" + noblanksvalue)
        person = self.conn.createURI("http://xmlns.com/foaf/0.1/Person")
        #value entered by user
        ob = self.conn.createLiteral(value)

        ## our subject is a person
        self.conn.add(subject, RDF.TYPE, person)
        ## our subject's name is the value supplied
        self.conn.add(subject, RDFS.LABEL, ob)

    def getvalues(self):
        endpoint = "http://" + AG_HOST + ":" + str(AG_PORT) + "/catalogs/" + AG_CATALOG + "/repositories/" + AG_REPOSITORY
        print endpoint
        query = sparqlquery.SparqlQuery(endpoint)
        results = query.runfullquery(self.value)
        self.query_string = query.querystring()
        return results

    def getquerystring(self):
        return self.query_string

    def close(self):
        self.conn.close();
        self.repo = self.conn.repository
        self.repo.shutDown()
