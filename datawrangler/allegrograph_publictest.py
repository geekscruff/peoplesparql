__author__ = 'geekscruff'
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from agraphpythonclient.src2.franz.openrdf.repository.repository import Repository
from agraphpythonclient.src2.franz.openrdf.query.query import QueryLanguage

AG_HOST = 'geekscruff.me'
AG_PORT = 10035
AG_CATALOG = 'public-catalog'
AG_REPOSITORY = 'artworld-people'
AG_USER = 'anonymous'
AG_PASSWORD = ''

"""
Can we connect to AG?
"""
print "Starting connection"
server = AllegroGraphServer(AG_HOST, AG_PORT)
print "Available catalogs", server.listCatalogs()
catalog = server.openCatalog(AG_CATALOG)  ## named catalog
accessMode = Repository.ACCESS
myRepository = catalog.getRepository(AG_REPOSITORY, accessMode)
conn = myRepository.getConnection()
print "Repository %s is up!  It contains %i statements." % (myRepository.getDatabaseName(), conn.size())

print "SPARQL query for all triples in repository."
try:
    queryString = "SELECT ?s ?o  WHERE {?s <http://dlib.york.ac.uk/ontologies/vocupper#hasName> ?o .}"
    tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, queryString)
    result = tupleQuery.evaluate()
    count = 0
    try:
        for bindingSet in result:
            s = bindingSet.getValue("s")
            o = bindingSet.getValue("o")
            count = count + 1
            print "%s %s" % (s, o)
    finally:
        print ("this (" + str(count) + ") many people")
        result.close()
finally:
    conn.close()
    myRepository = conn.repository
    myRepository.shutDown()