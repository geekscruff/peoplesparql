__author__ = 'geekscruff'

from flask import Blueprint, render_template, session, request, redirect, url_for

from querybuilder import sparqlquery
from datawrangler import add

research = Blueprint('research', __name__,
                     template_folder='templates')


@research.route('/query', defaults={'page': 'query'}, methods=['GET', 'POST'])
@research.route('/create', defaults={'page': 'create'}, methods=['GET', 'POST'])
@research.route('/<page>')
def show(page):
    if page == 'create':
        session.pop('json', None)
        if request.method == 'POST':
            addperson = add.Add()
            addperson.update(request.form['name'])
            results = addperson.getvalues()

            session['query'] = addperson.getquerystring()

            s = "<table><tr><td>subject</td><td>predicate</td><td>object</td></tr>"
            for result in results["results"]["bindings"]:
                s += "<tr><td>http://geekscruff.me/people/" + request.form['name'].replace(" ", "") + "</td><td>" + result["p"]["value"] + "</td><td>" + result["o"]["value"]  + "</td></tr>"
            s += "</table>"
            s += "<p>JSON OUTPUT <pre>" + str(results) + "</pre></p>"
            session['json'] = s

            addperson.close()

    elif page == 'query':
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
            session['query'] = query_string
            s = "<table><tr><td>subject</td><td>predicate</td><td>object</td></tr>"
            for result in results["results"]["bindings"]:
                s += "<tr><td>" + result["s"]["value"] + "</td><td>" + "http://www.w3.org/2000/01/rdf-schema#label" + "" \
                                                                                                                      "</td><td>" + \
                     result["o"]["value"] + "</td></tr>"
            s += "</table>"
            s += "<p>JSON OUTPUT <pre>" + str(results) + "</pre></p>"
            session['q'] = s

    elif page == 'explore':
        #don't do anything just now
        x = "nothing to do yet"

    return render_template('%s.html' % page)