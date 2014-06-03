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

    # Load production config from file, otherwise load the local config
    if os.path.isfile('/opt/peoplesparql/config.py'):
        logger.info("INFO research.py - loaded production config")
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

        # Display the query page
        s = ""
        discards = []
        try:
            logger.debug("DEBUG research.py -- using repository: " + app.config['AG_DATASOURCES'])
            # Get a list of endpoints to populate the list on the query page
            endpoints = endpointslist.EndpointsList().listall(app.config['AG_DATASOURCES'])

            # Build up the table to return to the query page as session['epl']
            for result in endpoints["results"]["bindings"]:
                s += '<tr><td><input name="' + result["s"]["value"] + '" type="checkbox" value="' + result["o"]["value"] + '">' + result["o"]["value"] + '</td></tr>'
            session['epl'] = s  # Return the table as a session variable

        except AttributeError as e:
            logger.error("AttributeError research.py - " + e.message)
            session['epl'] = "<tr><td>No endpoints have been setup.</td></tr>"
        except TypeError as e:
            logger.error("TypeError research.py - " + e.message)
            session['epl'] = "<tr><td>No endpoints have been setup.</td></tr>"

        if request.method == 'POST':  # If one of the forms has been POSTed from the query page

            # If we have a search term or a discard request, or a view more request
            if request.form.get('term', False) or request.form.get('discard', False) or request.form.get('more', False):

                eps = []  # list of endpoint urls

                # for a discard request, combine the existing discard options with the new ones
                if request.form.get('discard', False):
                    session.pop('q', None)
                    discards = session['discards']
                    discards += request.form.getlist('discard')
                    session['discards'] = discards
                    eps = session['eps']
                    resultslist = session['rl']

                elif request.form.get('term', False):
                    # for a search pop existing sessions
                    session.pop('q', None)
                    session.pop('discards', None)
                    session.pop('eps', None)
                    session.pop('more', None)
                    # start setting up results
                    session['query'] = "You searched for:<br />" + request.form['term']

                    session['ep'] = "In:<br />" # endpoint names

                    #get list of endpoint uris to query against
                    results = endpointslist.EndpointsList().listalluris(app.config['AG_DATASOURCES'])

                    for result in results["results"]["bindings"]:
                        # if the endpoint was seledcted add it to the eps list
                        if request.form.get(result["s"]["value"], False):
                            session['ep'] += request.form[result["s"]["value"]] + "<br />"
                            eps.append(result["s"]["value"])

                    # If no endpoints were selected
                    if session['ep'] == "In:<br />":
                        session['ep'] = "Please select one or more query target(s)"

                    session['eps'] = eps
                    session['discards'] = []

                    # Do each query in turn
                    # TODO ideally I'd like to stream the results dynamically

                    resultslist = []

                    # run the query on each endpoint, add to the list object
                    for e in eps:
                        # TODO get the AND from a form variable
                        # Run the name search
                        resultslist.append(sparql_query.SparqlQuery('AND', e).namesearch(request.form['term']))

                    # set session variable
                    session['rl'] = resultslist

                # if request is to view more, get the endpoint and id from the form variables and query
                elif request.form.get('more', False):
                    resultslist = session['rl']
                    eps = session['eps']
                    discards = session['discards']
                    session[request.form['q']] = sparql_query.SparqlQuery('AND', request.form['e']).allsearch(request.form['q'])

                d = '<form action="query" method=post>'

                count = 0
                for results in resultslist:
                # Process the results and return as a series of tables
                    table = '<div class="res"><p>From: ' + eps[count] + '</p>'

                    if results == "error" or results is None:
                        d += '<div class="res"><p>From: ' + eps[count] + '</p>' + \
                             '<p>Something went wrong with the connection to this endpoint</p></div>'
                    else:
                        table += '<table class="resultstable">'
                        for result in results["results"]["bindings"]:
                            if result["o"]["value"] not in discards:
                                table += '<tr><td>' + result["o"]["value"] + ' <span id="tiny">' \
                                         '(id: <a href="' + result["s"]["value"] + '">' + result["s"]["value"] + '</a>)</span>'

                                if session.get(result["s"]["value"]):
                                    table += '<div><table class="more">'
                                    for item in session[result["s"]["value"]]["results"]["bindings"]:
                                        table += '<tr><td>' + item["p"]["value"] + '</td>' \
                                            '<td>' + item["o"]["value"] + '</td></tr>'
                                    table += '</table></div>'
                                else:
                                    table += '<form action="query" method=post>' \
                                             '<input id="more" name="more" value="View More" type="submit">'\
                                             '<input name="q" value="' + result["s"]["value"] + '" type="hidden">' \
                                             '<input name="e" value="' + eps[count] + '" type="hidden">' \
                                             '</form>'
                                table += '</td><td style="width: 40px"><input type="checkbox" class="check" value="' + result["o"]["value"] + '" name="discard"></td></tr>'
                        if "<td>" not in table:
                            table += '<tr><td>There are no results</td></tr></table><br /></div>'
                        else:
                            table += '</table><br /></div>'
                        d += table

                        count += 1

                d += '<br /><input type="checkbox" id="selectall">Select / Deselect all</input>' \
                     '<br /><input type="submit" value="Discard checked items"></form>'
                session['q'] = d

            # If the add new endpoint form has been used
            elif request.form.get('name', False):
                session.pop('q', None)
                session.pop('ep', None)

                if request.form.get('uri', False):
                    try:
                        #setup the new endpoint
                        endpoint.Endpoint(request.form['uri']).setup_new_sparql_endpoint(request.form['name'])
                        session['query'] = "Endpoint: " + request.form['name'] + " added (" + request.form['uri'] + ")"
                    except Exception as e:
                        logger.error("ERROR! research.py - " + e.message)
                        session['query'] = "There was a problem setting up this endpoint, " \
                                           "please check your details and make sure you are connected to the Internet."

            # If the search is posted but nothing was entered, tell the user
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