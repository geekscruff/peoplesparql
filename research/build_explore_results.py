__author__ = 'geekscruff'

"""This class is a helper for research.py - it builds and returns results for the different 'explore' options"""

from flask import session
import logging
from datawrangler import add_triple, connect
from queryandexplore import sparql_query_specific, process_rdf, sparql_query_private
import rfc3987
import re
from guess_language import guessLanguageName
import requests
from franz.openrdf.repository.repositoryconnection import RDFFormat
from rdflib.graph import RDF, RDFS, Graph
import os

logger = logging.getLogger(__name__)


class BuildResults:
    def __init__(self, type):
        logger.debug("DEBUG build_explore_results.py -- object instantiated")
        self.sameas = []
        if type == 'explore':
            self.buildexploreresults()
            self.buildsameastable()
        elif type == 'enhance':
            self.buildenhancedresults()
            self.buildsameastable()
        elif type == 'dedup':
            self.builddedupresults()
            self.buildsameastable()

    # build the basic explore results
    def buildexploreresults(self):
        logger.debug("DEBUG build_explore_results.py -- buildexploreresults")
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()

        try:
            count = 0
            resultslist = session['resultslist']
            eps = session['endpoints']
            # We want a different display for the results in 'explore', so re-write them here
            table = ''
            for results in resultslist:
                for result in results["results"]["bindings"]:
                    if result["s"]["value"] + '--' + result["o"]["value"] not in session['discards']:

                        table += '<tr><td>' + result["o"]["value"] + \
                                 ' <span id="tiny"><br /><div class="reveal" style="display: none;">' \
                                 '<a target="_blank" href="' + result["s"]["value"] + '">' + result["s"][
                                     "value"] + '</a>'
                        table += '<br /><br /><table class="resultstable">'

                        # If the user is logged in, store results in tmp catalog
                        if session.get('email'):
                            addnew = add_triple.AddTriple(conn)
                            context = '<http://geekscruff.me/tmp#' + session['email'] + '>'
                            addnew.setcontexts([context])
                            logger.debug("DEBUG build_explore_results.py -- set context " + context)
                            addnew.setupsubject(result["s"]["value"])
                            session['store'] = 'yes'
                        else:
                            session['store'] = 'no'

                        for res in sparql_query_specific.SparqlQuery('AND', eps[count]).allsearch(result["s"]["value"], 'literal')["results"]["bindings"]:

                            if session.get('email'):
                                addnew.addliteral(res["p"]["value"], res["o"]["value"])

                            table += '<tr><td>' + res["p"]["value"] + '</td><td>'
                            if res["o"]["value"].startswith('http://www.getty'):
                                table += '<a href="' + res["o"]["value"] + '">Getty ULAN</a>' + '</td></tr>'
                            elif res["o"]["value"].startswith('http://'):
                                table += '<a href="' + res["o"]["value"] + '">' + res["o"][
                                    "value"] + '</a>' + '</td></tr>'
                            else:
                                table += res["o"]["value"] + '</td></tr>'

                        for res in \
                                sparql_query_specific.SparqlQuery('AND', eps[count]).allsearch(result["s"]["value"], 'uri')[
                                    "results"]["bindings"]:

                            if session.get('email'):
                                addnew.adduri(res["p"]["value"], res["o"]["value"])

                            table += '<tr><td>' + res["p"]["value"] + '</td><td>'
                            table += '<a href="' + res["o"]["value"] + '">' + res["o"]["value"] + '</a>' + '</td></tr>'

                            if res["p"]["value"].endswith('sameas') or res["p"]["value"].endswith('sameAs'):
                                self.sameas.append(res["o"]["value"])

                        table += "</table></div>"
                        table += '<br /></span></td></tr>'

                        conn.deleteDuplicates('spo')
                        conn.close()

                count += 1
            session['results'] = table

        # KeyError is thrown if the session does not exist
        except KeyError as e:
            logger.error("KeyError research.py - " + e.message + " (resultslist session isn't set)")
            session.pop('store', None)
            session.pop('epselect', None)
        except AttributeError as e:
            logger.error("AttributeError research.py - " + e.message + " (probably connection problem)")
            session.pop('store', None)
            session.pop('epselect', None)

    # build the 'enhanced' list
    def buildenhancedresults(self):
        logger.debug("DEBUG build_explore_results.py -- buildenhancedresults")
        table = session['results']
        session.pop('sameas')
        self.sameas = []
        enhancelist = session['enhancelist']
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
        lastone = 'new'

        #store enhanced data
        for results in enhancelist:
            for result in results["results"]["bindings"]:

                #If the user is logged in, store results in tmp catalog
                if session.get('email'):

                    addnew = add_triple.AddTriple(conn)
                    context = '<http://geekscruff.me/tmp#' + session['email'] + '>'
                    addnew.setcontexts([context])
                    logger.debug("DEBUG build_explore_results.py -- set context " + context)

                    if 'sameas' in result["p"]["value"] or 'sameAs' in result["p"]["value"]:
                        try:
                            if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                    self.sameas.append(result["o"]["value"])
                        except UnicodeEncodeError as e:
                                logger.error('UnicodeEncodeError - build_explore_results.py: ' + e.message)

                    addnew.setupsubject(result["s"]["value"])
                    # we want to only include english, guess language does a good job on short paragraphs
                    # filtering results would obviously be better but I had problems in filtering out too much
                    if str(rfc3987.match(result["o"]["value"], rule='URI')) == 'None':
                        if guessLanguageName(result["o"]["value"]) == 'English' or guessLanguageName(result["o"]["value"]) == 'UNKNOWN':
                        # proceed ...
                            try:
                                # we want to avoid foreign language dbpedia results so check for http://XX.dbpedia.org
                                if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                    if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                        session['store'] = 'yes'
                                        addnew.addliteral(result["p"]["value"], result["o"]["value"])

                            except UnicodeEncodeError as e:
                                logger.error('UnicodeEncodeError - build_explore_results.py: ' + e.message)
                    else:
                        if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(result["o"]["value"])):
                            if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                session['store'] = 'yes'
                                addnew.adduri(result["p"]["value"], result["o"]["value"])

                    conn.deleteDuplicates('spo')
                    conn.close()

                else:
                    session['store'] = 'no'

                if 'sameas' in result["p"]["value"] or 'sameAs' in result["p"]["value"]:
                    try:
                        if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(result["o"]["value"])):
                            if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(result["o"]["value"])):
                                self.sameas.append(result["o"]["value"])
                    except UnicodeEncodeError as e:
                         logger.error('UnicodeEncodeError - build_explore_results.py: ' + e.message)

                try:
                    if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(result["s"]["value"])):
                        if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(result["s"]["value"])):

                            if result["s"]["value"] != lastone:
                                if lastone != 'new':  # end last one
                                    table += '</table></div><br /></span></td></tr>'

                                # start new one
                                table += '<tr><td>' + result["s"]["value"] + ' <span id="tiny"><br /> ' \
                                         '<div class="reveal" style="display: none;">' \
                                         '<a target="_blank" href="' + result["s"][
                                         "value"] + '">' + \
                                         result["s"]["value"] + '</a>' \
                                                                '<br /><br /><table class="resultstable">'

                            if str(rfc3987.match(result["o"]["value"], rule='URI')) == 'None':
                                table += '<tr><td>' + result["p"]["value"] + '</td><td>' + result["o"]["value"] + '</td></tr>'
                            else:
                                table += '<tr><td>' + result["p"]["value"] + '</td><td><a href="' + result["o"]["value"] + '">' + \
                                             result["o"]["value"] + '</a></td></tr>'

                        lastone = result["s"]["value"]
                except UnicodeEncodeError as e:
                    logger.error('UnicodeEncodeError - build_explore_results.py: ' + e.message)

        # finish the very last one
        table += '</table></div><br /></span></td></tr>'

        session['results'] = table

    # build the cleaned up enhanced results
    def builddedupresults(self):
        logger.debug("DEBUG build_explore_results.py -- builddedupresults")
        conn = connect.Connect('tmp', cat="private-catalog").repoconn()

        resultslist = session['resultslist']

        table = ''
        done = ''
        for results_1 in resultslist:

            for r in results_1["results"]["bindings"]:
                go_on = True
                if 'dbpedia' in r["s"]["value"] and not 'http://dbpedia.org' in r["s"]["value"]:
                    go_on = False
                elif 'dbpedia' not in r["s"]["value"]:
                    go_on = True

                if go_on:

                    if r["s"]["value"] != done:
                        table += '<tr><td><h3>' + r["s"]["value"] + '</h3>'
                        table += '<span id="tiny"><a href="' + r["s"]["value"] + '">' + r["s"]["value"] + '</a></span><br />'
                        query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' \
                                'SELECT DISTINCT ?l FROM <http://geekscruff.me/tmp#' + session[
                                    'email'] + '> WHERE { <' + r["s"]["value"] + '> rdfs:label ?l'
                        results = sparql_query_private.QueryPrivate(conn, query + ' }').query()
                        if len(results) == 1:
                            for label in results:
                                table += label.getValue('l').getValue() + '<br />'
                        elif len(results) > 1:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                            res = sparql_query_private.QueryPrivate(conn, query + ' }').query()
                            if len(results) != 0:
                                for lab in res:
                                    table += lab.getValue('l').getValue() + '<br />'
                            else:
                                for label in results:
                                    table += label.getValue('l').getValue() + '<br />'

                        table += '<br/><table class="resultstable"'

                        query = 'SELECT DISTINCT ?p ?o FROM <http://geekscruff.me/tmp#' + session['email'] + '>' \
                                                                                                             ' WHERE { { <' + \
                                r["s"]["value"] + '> ?p ?o . FILTER ((isURI(?o))) } MINUS {<' + r["s"][
                                    "value"] + '> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o } MINUS {<' + \
                                r["s"]["value"] + '> <http://dbpedia.org/ontology/wikiPageExternalLink> ?o } }'

                        results = sparql_query_private.QueryPrivate(conn, query).query()

                        # fetch the rdf and process
                        # TODO this is very slow, so more thought on optimization is needed
                        for res in results:
                            try:
                                # this will skip anything that times out after 0.5s
                                requests.get(res.getValue('o').getValue(), timeout=0.5)

                                try:
                                    # hardcoded this in as links to bbc's 'your painting' were taking a minute
                                    # and we know they don't have rdf
                                    if 'bbc' not in res.getValue('o').getValue():
                                        #let's skip all non root dbpedia results
                                        if not re.match('^http\:\/\/\w\w\.dbpedia\.org', str(res.getValue('o').getValue())):
                                            if not re.match('^http\:\/\/\w\w\w\.dbpedia\.org', str(res.getValue('o').getValue())):

                                                if 'http://data.linkedmdb.org/resource' in str(res.getValue('o').getValue()):
                                                    uri = str(res.getValue('o').getValue()).replace('resource', 'data')
                                                    graph = process_rdf.ProcessRdf().fromuri(uri)
                                                else:
                                                    graph = process_rdf.ProcessRdf().fromuri(res.getValue('o').getValue())

                                                path = '/home/geekscruff/tmp.rdf'

                                                subgraph = Graph()

                                                subgraph += graph.triples((None, RDF.type, None))
                                                subgraph += graph.triples((None, RDFS.label, None))

                                                subgraph.serialize(destination=path)
                                                os.chmod(path, 0664)
                                                conn.addFile(filePath=path, format=RDFFormat.RDFXML,
                                                             context='<http://geekscruff.me/tmp#' + session['email'] + '>',
                                                             serverSide=True)

                                except Exception as e:
                                    logger.error('ERROR! -- build_explore_results.py: skip this one, message: ')
                                    logger.error(e.message)
                                    table += '</td></tr>'

                            except Exception as e:
                                logger.error('ERROR! -- build_explore_results.py: skip this one, message: ')
                                logger.error(e.message)

                        # Show basic info
                        query = 'SELECT DISTINCT ?p ?l FROM <http://geekscruff.me/tmp#' + session['email'] + '> WHERE { <' + \
                                r["s"]["value"] + '> ?p ?l . FILTER ((isLiteral(?l))) }'
                        info = sparql_query_private.QueryPrivate(conn, query).query()

                        if info:
                            table += '<tr><td colspan="2"><h4>BASIC INFO</h4></td></tr>'
                            for p in info:
                                if guessLanguageName(p.getValue('l').getValue()) == 'English' or guessLanguageName(
                                        p.getValue('l').getValue()) == 'UNKNOWN':
                                    table += '<tr><td>' + p.getValue('p').getValue() + '</td>'
                                    table += '<td>' + p.getValue('l').getValue() + '</td></tr>'

                        # Show related people
                        query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?v ?p ?l FROM <http://geekscruff.me/tmp#permanentdata> FROM <http://geekscruff.me/tmp#' + \
                                session['email'] + '> WHERE { { <' + r["s"][
                                    "value"] + '> ?p ?v . FILTER ((isURI(?v))) . ?v a ?t . ?t rdfs:subClassOf <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent> . OPTIONAL { ?v rdfs:label ?l } '
                        if 'dbpedia' in r["s"]["value"]:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                        query += '} }'
                        people = sparql_query_private.QueryPrivate(conn, query).query()

                        if people:
                            table += '<tr><td colspan="2"><h4>RELATED PEOPLE, GROUPS AND ORGANISATIONS</h4></td></tr>'
                            for p in people:
                                table += '<tr style="background: #f0d6d6"><td>' + p.getValue('p').getValue() + '</td>'
                                table += '<td><a href="' + p.getValue('v').getValue() + '">'
                                if p.getValue('l') is not None:
                                    table += p.getValue('l').getValue()
                                else:
                                    table += p.getValue('v').getValue()
                                table += '</a></td></tr>'

                        # related places

                        query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?v ?p ?l FROM <http://geekscruff.me/tmp#permanentdata> FROM <http://geekscruff.me/tmp#' + \
                                session['email'] + '> WHERE { { <' + r["s"][
                                    "value"] + '> ?p ?v . FILTER ((isURI(?v))) . ?v a ?t . ?t rdfs:subClassOf <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Place> . OPTIONAL { ?v rdfs:label ?l } '
                        if 'dbpedia' in r["s"]["value"]:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                        query += '} }'
                        places = sparql_query_private.QueryPrivate(conn, query).query()
                        if places:
                            table += '<tr><td><h4>RELATED PLACES</h4></td></tr>'
                            for p in places:
                                table += '<tr style="background: #BCEE68"><td>' + p.getValue('p').getValue() + '</td>'
                                table += '<td><a href="' + p.getValue('v').getValue() + '">'
                                if p.getValue('l') is not None:
                                    table += p.getValue('l').getValue()
                                else:
                                    table += p.getValue('v').getValue()
                                table += '</a></td></tr>'

                        # related events
                        query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?v ?p ?l FROM <http://geekscruff.me/tmp#permanentdata> FROM <http://geekscruff.me/tmp#' + \
                                session['email'] + '> WHERE { { <' + r["s"][
                                    "value"] + '> ?p ?v . FILTER ((isURI(?v))) . ?v a ?t . ?t rdfs:subClassOf <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Event> . OPTIONAL { ?v rdfs:label ?l } '
                        if 'dbpedia' in r["s"]["value"]:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                        query += '} }'
                        events = sparql_query_private.QueryPrivate(conn, query).query()
                        if events:
                            table += '<tr><td><h4>EVENTS</h4></td></tr>'
                            for p in events:
                                table += '<tr style="background: #F0E68C"><td>' + p.getValue('p').getValue() + '</td>'
                                table += '<td><a href="' + p.getValue('v').getValue() + '">'
                                if p.getValue('l') is not None:
                                    table += p.getValue('l').getValue()
                                else:
                                    table += p.getValue('v').getValue()
                                table += '</a></td></tr>'

                        # related subjects / concepts
                        query = 'SELECT DISTINCT ?v ?l FROM <http://geekscruff.me/tmp#' + session['email'] + '> WHERE { <' + \
                                r["s"]["value"] + '> <http://purl.org/dc/terms/subject> ?v . OPTIONAL { ?v rdfs:label ?l } '
                        if 'dbpedia' in r["s"]["value"]:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                        query += ' }'
                        subs = sparql_query_private.QueryPrivate(conn, query).query()

                        if subs:
                            table += '<tr><td colspan="2"><h4>SUBJECTS</h4></td></tr>'
                            for p in subs:
                                table += '<tr style="background: #87CEFF"><td>http://purl.org/dc/terms/subject</td>'
                                table += '<td><a href="' + p.getValue('v').getValue() + '">'
                                if p.getValue('l') is not None:
                                    table += p.getValue('l').getValue()
                                else:
                                    table += p.getValue('v').getValue()
                                table += '</a></td></tr>'

                        # works and objects
                        query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?v ?p ?l FROM <http://geekscruff.me/tmp#permanentdata> FROM <http://geekscruff.me/tmp#' + \
                                session['email'] + '> WHERE { { <' + r["s"][
                                    "value"] + '> ?p ?v . FILTER ((isURI(?v))) . ?v a ?t . ?t rdfs:subClassOf owl:Thing . OPTIONAL { ?v rdfs:label ?l } '
                        if 'dbpedia' in r["s"]["value"]:
                            query += '. FILTER langMatches(lang(?l),"en" )'
                        query += '} }'

                        things = sparql_query_private.QueryPrivate(conn, query).query()
                        if things:
                            table += '<tr><td><h4>RELATED WORKS, OBJECTS AND THINGS</h4></td></tr>'
                            for p in things:
                                table += '<tr style="background: #B0E0E6"><td>' + p.getValue('p').getValue() + '</td>'
                                table += '<td><a href="' + p.getValue('v').getValue() + '">'
                                if p.getValue('l') is not None:
                                    table += p.getValue('l').getValue()
                                else:
                                    table += p.getValue('v').getValue()
                                table += '</a></td></tr>'

                        table += '</td></tr></table></tr>'
                    else:
                        table += '</table></tr>'


                conn.deleteDuplicates('spo')
                conn.close()
                done = r["s"]["value"]
            session['results'] = table

    # build the sameas table for display
    def buildsameastable(self):
        logger.debug("DEBUG build_explore_results.py -- buildsameastable")
        if self.sameas:
            session['sameas'] = self.sameas
        elif session.get('sameas'):
            self.sameas = session.get('sameas')

        sameastable = '<div class="res"><br /><table class="resultstable">'
        for s in self.sameas:
            if s not in sameastable:
                sameastable += '<tr><td><a href="' + s + '">' + s + '</a></td></tr>'
        sameastable += '</table><br /></div>'
        session['sameastable'] = sameastable
