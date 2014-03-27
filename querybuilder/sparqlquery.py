__author__ = 'geekscruff'

from SPARQLWrapper import SPARQLWrapper, JSON


class SparqlQuery:
    def __init__(self, sparql):
        self.sparql = sparql
        self.query_string = ""

    def runquery(self):

        if self.sparql == "http://collection.britishmuseum.org/sparql":
            person = "http://erlangen-crm.org/current/E21_Person"
        elif self.sparql == "http://geekscruff.me:10035/catalogs/public-catalog/repositories/artworld-people":
            person = "http://www.w3.org/2002/07/owl#NamedIndividual"
        else:
            person = "http://xmlns.com/foaf/0.1/Person"
            #DNB is throwing an error if I add ORDER BY ASC(?o) (not sure why - sparql version perhaps?)
        sparqlquery = SPARQLWrapper(self.sparql)
        self.query_string = "SELECT DISTINCT ?s ?o { ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o . ?s ?p <" \
                            + person + ">}  LIMIT 100"
        sparqlquery.setQuery(self.query_string)
        sparqlquery.setReturnFormat(JSON)
        results = sparqlquery.query().convert()
        return results

    def querystring(self):
        return self.query_string