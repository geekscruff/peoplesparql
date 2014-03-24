__author__ = 'geekscruff'

from flask import Blueprint, render_template, abort, session, request
from jinja2 import TemplateNotFound
from SPARQLWrapper import SPARQLWrapper, JSON

query = Blueprint('query', __name__,
                  template_folder='templates')

#@query.route('/query', defaults={'page': 'query'})
#@query.route('/<page>')
#Query page
@query.route('/query', defaults={'page': 'query'}, methods=['GET', 'POST'])
@query.route('/<page>')
def show(page):
    if page == 'query':
    #destroy the existing query session on page load
        session.pop('q', None)
        #if the query button is clicked, replace it with the sparql query result
        #TODO error handling
        if request.method == 'POST':

            if request.form['sparql'] == "http://collection.britishmuseum.org/sparql":
                person = "http://erlangen-crm.org/current/E21_Person"
            elif request.form[
                'sparql'] == "http://geekscruff.me:10035/catalogs/public-catalog/repositories/artworld-people":
                person = "http://www.w3.org/2002/07/owl#NamedIndividual"
            else:
                person = "http://xmlns.com/foaf/0.1/Person"
            #DNB is throwing an error if I add ORDER BY ASC(?o) (not sure why - sparql version perhaps?)
            sparql = SPARQLWrapper(request.form['sparql'])
            query_string = "SELECT DISTINCT ?s ?o { ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o . ?s ?p <" \
                           + person + ">}  LIMIT 100"
            sparql.setQuery(query_string)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            s = "<p>QUERY (example from " + request.form['sparql'] + ")</p><pre>" + query_string + "</pre>"
            s += "<p>RESULTS</p><table><tr><td>subject</td><td>predicate</td><td>object</td></tr>"

            for result in results["results"]["bindings"]:
                s += "<tr><td>" + result["s"]["value"] + "</td><td>" + "http://www.w3.org/2000/01/rdf-schema#label" + "" \
                                                                                                                      "</td><td>" + \
                     result["o"]["value"] + "</td></tr>"
            s += "</table>"
            s += "<p>FULL JSON <pre>" + str(results) + "</pre></p>"
            session['q'] = s
    return render_template('%s.html' % page)