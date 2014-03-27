__author__ = 'geekscruff'

from flask import Blueprint, render_template, session, request

from querybuilder import sparqlquery

research = Blueprint('research', __name__,
                  template_folder='templates')

@research.route('/query', defaults={'page': 'query'}, methods=['GET', 'POST'])
@research.route('/<page>')
def show(page):
    if page == 'query':
    #destroy the existing query session on page load
        session.pop('q', None)
        #if the query button is clicked, replace it with the sparql query result
        #TODO error handling
        if request.method == 'POST':

            #use the SparqlQuery class to run a query
            doquery = sparqlquery.SparqlQuery(request.form['sparql'])
            results = doquery.runquery()
            query_string = doquery.query_string

            #print the results
            s = "<p>query (example from " + request.form['sparql'] + ")</p><pre>" + query_string + "</pre>"
            s += "<p>RESULTS</p><table><tr><td>subject</td><td>predicate</td><td>object</td></tr>"
            for result in results["results"]["bindings"]:
                s += "<tr><td>" + result["s"]["value"] + "</td><td>" + "http://www.w3.org/2000/01/rdf-schema#label" + "" \
                                                                                                                      "</td><td>" + \
                     result["o"]["value"] + "</td></tr>"
            s += "</table>"
            s += "<p>FULL JSON <pre>" + str(results) + "</pre></p>"
            session['q'] = s

    return render_template('%s.html' % page)