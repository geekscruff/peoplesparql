__author__ = 'geekscruff'

from querybuilder import endpointslist, sparql_query, endpoint
from flask import Blueprint, render_template, session, request, redirect, url_for, Flask, current_app
import os
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

research = Blueprint('research', __name__, template_folder='templates')

@research.route('/query', defaults={'page': 'query'}, methods=['GET', 'POST'])
@research.route('/create', defaults={'page': 'create'}, methods=['GET', 'POST'])
@research.route('/<page>')
def show(page):

    if os.path.isfile('/opt/peoplesparql/config.py'):
        logger.info("INFO research.py - loaded production config")
        # Load production config from file
        app.config.from_pyfile('/opt/peoplesparql/config.py', silent=False)
    else:
        logger.info("INFO research.py - loaded local config")
        app.config.from_object('peoplesparql')

    if page == 'create':
        session.pop('json', None)
        if request.method == 'POST':
            session['query'] = "create functionality has not been added yet"
            # addperson = add.Add()
            # addperson.update(request.form['name'])
            # results = addperson.getvalues()
            #
            # session['query'] = addperson.getquerystring()
            #
            # s = "<table><tr><td>subject</td><td>predicate</td><td>object</td></tr>"
            # for result in results["results"]["bindings"]:
            #     s += "<tr><td>http://geekscruff.me/people/" + request.form['name'].replace(" ", "") + "</td><td>" + \
            #          result["p"]["value"] + "</td><td>" + result["o"]["value"] + "</td></tr>"
            # s += "</table>"
            # session['json'] = s
            #
            # addperson.close()

    elif page == 'query':
        # If the query button is clicked, replace it with the sparql query result

        s = ""
        try:
            logger.debug("DEBUG research.py -- using repository: " + app.config['AG_DATASOURCES'])
            # Get a list of endpoints to populate the list on the query page
            endpoints = endpointslist.EndpointsList().listall(app.config['AG_DATASOURCES'])

            # Build up the table to return to the query page
            for result in endpoints["results"]["bindings"]:
                s += '<tr><td><input name="' + result["s"]["value"] + '" type="checkbox" value="' + result["o"]["value"] + '">' + result["o"]["value"] + '</td></tr>'
            session['eps'] = s  # Return the table as a session variable

        except AttributeError as e:
            logger.error("AttributeError research.py - " + e.message)
            session['eps'] = "<tr><td>No endpoints have been setup.</td></tr>"
        except TypeError as e:
            logger.error("TypeError research.py - " + e.message)
            session['eps'] = "<tr><td>No endpoints have been setup.</td></tr>"

        if request.method == 'POST':  # If one of the forms has been POSTed from the query page

            # If we have a search term, get the search term and endpoint(s) selected
            if request.form.get('term', False):
                session['query'] = "You searched for:<br />" + request.form['term']

                session['ep'] = "In:<br />" # endpoint names
                eps = [] # list of endpoint urls

                results = endpointslist.EndpointsList().listalluris(app.config['AG_DATASOURCES'])

                for result in results["results"]["bindings"]:
                    if request.form.get(result["s"]["value"], False):
                        session['ep'] += request.form[result["s"]["value"]] + "<br />"
                        eps.append(result["s"]["value"])

                if session['ep'] == "In:<br />":
                    session['ep'] = "Please select one or more query target(s)"

                # Do each query in turn
                # TODO ideally I'd like to stream the results dynamically
                d = ""
                for e in eps:
                    # TODO get the AND from a form variable

                    # Run the name search
                    results = sparql_query.SparqlQuery('AND', e).namesearch(request.form['term'])

                    # Process the results
                    table = '<p>Results from: ' + e + '</p>'

                    if results == "error" or results == None:
                        d += '<p>Results from: ' + e + '</p>' + '<p>Something went wrong with the connection to this endpoint</p>'

                    elif "[]" not in str(results):
                        table += '<table>'
                        for result in results["results"]["bindings"]:
                            table += '<tr><td>' + result["o"]["value"] + ' <span id="tiny">(id: ' + result["s"]["value"] + ')</span></td></tr>'
                        table += '</table>'
                        d += table

                    else:  # Otherwise we can assume the query ran OK but that we got no results
                        d += '<p>There were 0 results from ' + e + '</p>'

                    session['q'] = d

            # If the add new endpoint form has been used
            elif request.form.get('name', False):
                session.pop('q', None)
                session.pop('ep', None)

                if request.form.get('uri', False):
                    try:
                        endpoint.Endpoint(request.form['uri']).setup_new_sparql_endpoint(request.form['name'])
                        session['query'] = "Endpoint: " + request.form['name'] + " added (" + request.form['uri'] + ")"
                    except Exception as e:
                        logger.error("ERROR! research.py - " + e.message)
                        session['query'] = "There was a problem setting up this endpoint, please check your details and make sure you are connected to the Internet."

            else:
                session['query'] = "You didn't supply the right information, please start over."

            # TODO Put some dynamic stuff in place to show query progress
            # TODO Give number of results and have each one open to show more
            # TODO EXTENSION - have a stab at sameas inferencing


        # Destroy the existing query sessions on clicking 'new'
        else:
            session.pop('q', None)
            session.pop('query', None)
            session.pop('ep', None)

    elif page == 'explore':
        #don't do anything just now
        return "nothing to do yet"

    return render_template('%s.html' % page)