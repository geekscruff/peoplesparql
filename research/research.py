__author__ = 'geekscruff'

"""the blueprint for handling query, explore and create pages"""

import same_person
from queryandexplore import endpoints_list, sparql_query_specific, endpoint, process_rdf
from datawrangler import connect, delete_triples
from flask import Blueprint, render_template, session, request, Flask
import os
import logging
import build_explore_results
import json
import re

logger = logging.getLogger(__name__)

app = Flask(__name__)

research = Blueprint('research', __name__, template_folder='templates')

@research.route('/query', defaults={'page': 'query'}, methods=['GET', 'POST'])
@research.route('/explore', defaults={'page': 'explore'}, methods=['GET', 'POST'])
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

    elif page == 'query':

        # Display the query page
        s = ""
        discards = []
        try:
            logger.debug("DEBUG research.py -- using repository: " + app.config['AG_DATASOURCES'])
            # Get a list of endpoints to populate the list on the query page
            endpoints = endpoints_list.EndpointsList().listall(app.config['AG_DATASOURCES'])

            # Build up the table to return to the query page as session['endpointslist']
            for result in endpoints["results"]["bindings"]:
                s += '<tr><td><input name="' + result["s"]["value"] + '" type="checkbox" value="' + result["o"]["value"] + '">' + result["o"]["value"] + '</td></tr>'
            session['endpointslist'] = s  # Return the table as a session variable

        except AttributeError as e:
            logger.error("AttributeError research.py - " + e.message)
            session['endpointslist'] = "<tr><td>No endpoints have been setup.</td></tr>"
        except TypeError as e:
            logger.error("TypeError research.py - " + e.message)
            session['endpointslist'] = "<tr><td>No endpoints have been setup.</td></tr>"

        if request.method == 'POST':  # If one of the forms has been POSTed from the query page

            # If we have a search term or a discard request
            if request.form.get('term', False) or request.form.get('discard', False) or request.form.get('cancel', False):

                eps = []  # list of endpoint urls

                # to get rid of the discards selection
                if request.form.get('cancel', False):
                    session.pop('discards')
                    session.pop('results', None)
                    discards = []
                    # this needs re-writing
                    resultslist = session['resultslist']
                    eps = session['endpoints']

                # for a discard request, combine the existing discard options with the new ones
                elif request.form.get('discard', False):
                    session.pop('results', None)
                    # this would fail if session exceeds a certain size,
                    # see http://stackoverflow.com/questions/15552418/flask-session-forgets-entry-between-requests
                    # solution implemented http://flask-kvsession.readthedocs.org/en/0.2/
                    if session.get('discards'):
                        discards = session['discards']
                    discards += request.form.getlist('discard')
                    session['discards'] = discards
                    eps = session['endpoints']
                    # we need to rewrite these
                    resultslist = session['resultslist']
                    tmp = []
                    for res in resultslist:
                        for r in res["results"]["bindings"]:
                            for d in discards:
                                sp = d.split('--')

                                if sp[0] in r["s"]["value"]:
                                    tmp.append(r)
                    for res in resultslist:
                        try:
                            for t in tmp:
                                res["results"]["bindings"].remove(t)
                        except ValueError as e:
                            logger.error('ValueError -- research.py: ' + e.message)

                    session['resultslist'] = resultslist

                elif request.form.get('term', False):
                    # for a search pop existing sessions
                    session.pop('results', None)
                    session.pop('discards', None)
                    session.pop('epselect', None)
                    session.pop('endpoints', None)
                    session.pop('resultslist', None)
                    session.pop('enhance', None)
                    session.pop('dedup', None)
                    session.pop('stored', None)

                    # start setting up results
                    session['query'] = request.form['term']

                    session['epselect'] = "In:<br />" # endpoint names

                    #get list of endpoint uris to query against
                    results = endpoints_list.EndpointsList().listalluris(app.config['AG_DATASOURCES'])

                    for result in results["results"]["bindings"]:
                        # if the endpoint was seledcted add it to the eps list
                        if request.form.get(result["s"]["value"], False):
                            session['epselect'] += request.form[result["s"]["value"]] + "<br />"
                            eps.append(result["s"]["value"])

                    # If no endpoints were selected
                    if session['epselect'] == "In:<br />":
                        session['epselect'] = "Please select one or more query target(s)"

                    session['endpoints'] = eps
                    session['discards'] = []

                    # Do each query in turn
                    # TODO ideally I'd like to stream the results dynamically

                    resultslist = []

                    # run the query on each endpoint, add to the list object
                    for e in eps:
                        # TODO extend query options, get the AND from a form variable
                        # Run the name search
                        res = sparql_query_specific.SparqlQuery('AND', e).namesearch(request.form['term'])

                        if res not in resultslist:
                            resultslist.append(res)

                    # set session variable
                    session['resultslist'] = resultslist

                # Process the results and return as a series of tables
                d = ''

                count = 0
                for results in resultslist:

                    table = '<div class="res"><p>From: ' + eps[count] + '</p>'

                    if results == "error" or results is None:
                        d += '<div class="res"><p>From: ' + eps[count] + '</p>' + \
                             '<p>Something went wrong with the connection to this endpoint</p></div>'
                    else:
                        table += '<table class="resultstable">'
                        for result in results["results"]["bindings"]:
                            if result["s"]["value"] + '--' + result["o"]["value"] not in discards:
                                table += '<tr><td>' + result["o"]["value"] + \
                                         ' <span id="tiny"><br />More details: ' \
                                         '<a target="_blank" href="' + result["s"]["value"] + '">' + result["s"]["value"] + '</a>' \
                                         '</span></td><td style="width: 40px">' \
                                         '<input type="checkbox" class="check" value="' + result["s"]["value"] + '--' + result["o"]["value"] + '" ' \
                                         'name="discard"></td></tr>'
                        if "<td>" not in table:
                            table += '<tr><td>There are no results</td></tr></table><br /></div>'
                        else:
                            table += '</table><br /></div>'
                        d += table

                        count += 1

                session['results'] = d

            # If the add new endpoint form has been used
            elif request.form.get('name', False):
                session.pop('results', None)
                session.pop('epselect', None)
                session.pop('endpoints', None)
                session.pop('resultslist', None)
                session.pop('query', None)
                session.pop('discards', None)

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
            # TODO Give number of results

        # Destroy the existing query sessions and temporary data on clicking 'new'
        else:
            session.pop('results', None)
            session.pop('epselect', None)
            session.pop('endpoints', None)
            session.pop('resultslist', None)
            session.pop('query', None)
            session.pop('discards', None)
            session.pop('sameas', None)
            session.pop('sameperson', None)
            session.pop('store', None)
            session.pop('enhancelist', None)

            # remove data for this user from the temporary repository
            if session.get('email'):
                conn = connect.Connect('tmp', cat='private-catalog').repoconn()
                delete_triples.DeleteTriples(conn).delete_all('<http://geekscruff.me/tmp#' + session['email'] + '>')
                conn.close()

    elif page == 'explore':
        # Get rid of sessions that are no longer needed
        session.pop('query', None)

        if not session.get('enhance') and not session.get('store'):
            build_explore_results.BuildResults('explore')

        if request.method == 'POST':

            if request.form.get('dedup', False):
                session['dedup'] = 'yes'
                build_explore_results.BuildResults('dedup')

            elif request.form.get('enhance', False):
                session.pop('enhance', None)
                session.pop('enhancelist', None)
                session.pop('dedup', None)

                # get rdf for all sameas results if possible, store
                if session.get('email'):
                    session['enhance'] = 'yes'
                    enhancelist = []
                    sameas = session['sameas']
                    for s in sameas:
                        try:
                            if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(s)):
                                if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(s)):
                                    g = process_rdf.ProcessRdf().fromuri(s)
                                    results = g.query('SELECT * {<' + s + '> ?p ?o . ?s ?p ?o} ORDER BY ?p')
                                    resultslist = g.query('select distinct ?s ?l { <' + s + '> ?p ?o . ?s ?p ?o . OPTIONAL { <' + s + '> rdfs:label ?l } }')

                                    jsonrl = json.loads(resultslist.serialize(format="json"))

                                    # let's load and store the graph
                                    # we store EVERYTHING, that might not be a good idea
                                    # alternate code in buildresults is more choosy
                                    # path = '/home/geekscruff/tmp.rdf'
                                    # g.serialize(destination=path)
                                    # os.chmod(path, 0664)
                                    # conn = connect.Connect('tmp', cat='private-catalog').repoconn()
                                    # conn.addFile(filePath=path, format=RDFFormat.RDFXML, context='<http://geekscruff.me/tmp#' + session['email'] + '>', serverSide=True)
                                    # os.remove(path)
                                    # conn.deleteDuplicates('spo')
                                    # conn.close()

                                    j = json.loads(results.serialize(format="json"))

                                    if j not in enhancelist:
                                        enhancelist.append(j)

                                    if jsonrl:
                                        session['resultslist'].append(jsonrl)

                        except Exception as e:
                            logger.error("ERROR! research.py - calling method caught raised " + e.message + '(uri was' + s + ')')
                    # if we have some results
                    if enhancelist:
                        session['store'] = 'yes'
                        session['enhancelist'] = enhancelist
                        build_explore_results.BuildResults('enhance')
                    #if the list is empty
                    else:
                        session['enhance'] = 'fail'
                        session['store'] = 'no'
                else:
                    if not session.get('enhance'):
                        session['enhance'] = 'no'
                        session['store'] = 'no'


            elif request.form.get('sameperson', False):

                #To find out how many items there are in the results list
                # not using this at the moment
                count = 0
                for res in session['resultslist']:
                    for r in res["results"]["bindings"]:
                        count += 1

                # sameperson count return the confidence, sameas, then replaced by names, then dates
                # then combine
                # need to pass the number to start at, so each number up to one less than the count
                # also need to pass the number to end at
                # ie 1,2, 1,3, 1,4 etc. then 2,3, then 3,4
                # 14 results would take
                # default will be

                listp = session['resultslist']
                sp = same_person.SamePerson(listp, '<http://geekscruff.me/tmp#' + session['email'] + '>')
                sameperson = sp.first_pass()
                session['confidence'] = sp.getconfidence()
                persons = '<p>'
                for item in sameperson:
                    i_list = item.split('--')
                    for i in i_list:
                        persons += i + '<br />'
                persons += '</div>'
                session['sameperson'] = persons
                # now we repeat with the rest and add to sameperson session
                # we could also have a confidence score alone I think

            if request.form.get('discard', False):
                discards = session['discards']
                discards += request.form.getlist('discard')
                session['discards'] = discards
                build_explore_results.BuildResults('explore')


    return render_template('%s.html' % page)


