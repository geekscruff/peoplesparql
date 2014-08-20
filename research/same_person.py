__author__ = 'geekscruff'


"""Compares two people to determine if they are the same"""

from queryandexplore import process_rdf, sparql_query_private
from datawrangler import connect, add_triple
from rdflib import ConjunctiveGraph
import json
import logging
import name_tools

logger = logging.getLogger(__name__)

# Limitations: only works on two names
# TODO proper report returned--add logging--dates to years--storing data--
# what else could we do here? thirdpass looking at places / subjects
# TODO improve commenting and logging


class SamePerson:
    def __init__(self, list, context=None, start=1, end=2):
        self.list = list # list of values to check
        self.value1 = None
        self.value2 = None
        self.value1label = None
        self.value2label = None
        self.dates1 = None
        self.dates2 = None
        self.start = start # point in the list to start
        self.end = end # point in the list to end
        self.contexts = context
        self.match = []
        self.overallconfidence = None
        self.listcount = 1


        # setup the two values
        for item in list:
            for l in item["results"]["bindings"]:

                # TODO check if these two blocks are essentially duplicating each other
                if len(self.list) >= 2:
                    if self.listcount == self.start:
                        self.value1 = l["s"]["value"]
                        self.value1label = l["o"]["value"]
                    elif self.listcount == self.end:
                        self.value2 = l["s"]["value"]
                        self.value2label = l["o"]["value"]
                    else:
                        logger.info(l["s"]["value"] + ' (' + l["s"]["value"] + ') not checked')

                else:
                    if self.listcount == self.start:
                        self.value1 = l["s"]["value"]
                        self.value1label = l["o"]["value"]
                    elif self.listcount == self.end:
                        self.value2 = l["s"]["value"]
                        self.value2label = l["o"]["value"]
                    else:
                        logger.info(l["s"]["value"] + ' (' + l["s"]["value"] + ') not checked')

                self.listcount += 1

    # first pass at a comparison
    def first_pass(self):

        # first check for an explicit same as
        if self.value1 and self.value2:
            self.match.append('match= ' + self.value1 + ' and ' + self.value2 + ' --')
            if self.sameas(self.value1, self.value2):
                self.match.append('match-sameas--confidence=' + str(
                    1.0) + '--There is an explicit sameas (or equivalent) relationship between ' + self.value1label + ' (' + self.value1 + ') and ' + self.value2label + ' (' + self.value1 + '). These are the same person.--')
                self.overallconfidence = 1.0
                return self.match
            # if no explicit sameas is in place, check the names
            else:
                self.match.append('match-sameas--There is no explicit sameas relationship between ' + self.value1label + ' (' + self.value1 + ') and ' + self.value2label + ' (' + self.value2 + '). Invstigate further ... --')
                names1 = self.checkname(self.value1, 1)
                names2 = self.checkname(self.value2, 2)
                scores = []

                if names1 and names2:
                    for nm in names1:
                        for n in names2:
                            # get a confidence score using name_tools
                            scores.append(name_tools.match(name_tools.canonicalize(nm), name_tools.canonicalize(n)))
                    confidence = 0
                    for score in scores:
                        if score > confidence:
                            confidence = score
                        if confidence >= 0.75:
                            self.match.append('match-name--confidence=' + str(
                                confidence) + '--The names are alike. Checking for dates ... --')
                        elif confidence < 0.75 and confidence > 0.5:
                            self.match.append('match-name--confidence=' + str(
                                confidence) + '--The names have some similarities, they could be the same person. Checking dates to be sure ... --')
                        elif confidence < 0.5:
                            self.match.append('match-name--confidence=' + str(
                                confidence) + '--The names are different, indicating that these are not likely to be the same person. Checking dates to be sure ... --')
                        self.overallconfidence = score

                        # check the dates
                        self.dates1 = self.checkdates(self.value1)

                        self.dates2 = self.checkdates(self.value2)

                        # if there are no dates for either check for sameas links to other sources
                        if not self.dates1 and not self.dates2:
                            self.match.append('match-dates--Neither of the names have associated dates. Checking for sameas links to other sources ... )' + '--')
                            # run a second pass on value 1
                            dates = self.secondpass(self.value1)
                            if dates:
                                for d in dates:
                                    self.dates1 = d
                                    self.match.append(
                                        'match-dates--These dates were found: ' + d + ' but there is nothing to compare them to--')

                            else:
                                self.match.append(
                                    'match-dates--No dates were found for ' + self.value1label + ' (' + self.value1 + ')--')

                            # run a second pass on value 2
                            dates = self.secondpass(self.value2)
                            if dates:
                                for d in dates:
                                    self.dates2 = d
                                    if self.dates1 and d in self.dates1:
                                        self.match.append(
                                            'match-dates--confidence=1.0--There is an exact match with birth and death dates (' + str(d) + ' and ' + str(self.dates1) + '). These are very likely the same person.--')
                                    elif self.dates1 and d not in self.dates1:
                                        self.match.append(
                                            'match-dates--confidence=0--The dates do not match (' + str(d) + ' and ' + str(self.dates1) +'). These are not likely to be the same person.--')
                                    else:
                                        self.match.append(
                                            'match-dates--These dates were found: ' + d + ' but there is nothing to compare them to--')

                            else:
                                self.match.append(
                                    'match-dates--No dates were found for ' + self.value2label + ' (' + self.value2 + ')--')
                                #return self.match
                            return self.match

                        # if there is one date, look for sameas links for the other
                        elif not self.dates1 and self.dates2:
                            self.match.append('match-dates--There are no birth or death dates for ' + self.value1label + ' (' + self.value1 + '). Checking for sameas links to other sources ... --')
                            # we could have more than one
                            dates = self.secondpass(self.value1)
                            if dates:
                                for d in dates:
                                    if d in self.dates2:
                                        self.match.append(
                                            'match-dates--confidence=1.0--There is an exact match with birth and death dates (' + str(d) + ' and ' + str(self.dates2) + '). These are very likely the same person.--')
                                        self.overallconfidence = 1.0
                                        return self.match
                                else:

                                    self.match.append(
                                        'match-dates--confidence=0--The dates do not match (' + str(d) + ' and ' + str(self.dates2) +'). These are not likely to be the same person.--')
                                    self.overallconfidence = 0
                                    return self.match

                            else:
                                self.match.append(
                                    'match-dates--confidence=0--We only have one date (' + str(self.dates2) + ') and nothing to compare it to.--')
                                self.overallconfidence = 0
                                return self.match

                        # if there is one date, look for sameas links for the other
                        elif not self.dates2 and self.dates1:
                            self.match.append('match-dates--There are no birth or death dates for ' + self.value2label + ' (' + self.value2 + '). Checking for sameas links to other sources ... --')
                            dates = self.secondpass(self.value2)
                            if dates:
                                for d in dates:
                                    if d in self.dates1:
                                        self.match.append(
                                            'match-dates--confidence=1.0--There is an exact match with birth and death dates (' + str(self.dates1) + ' and ' + str(d) + '). These are very likely the same person.--')
                                        self.overallconfidence = 1.0
                                        return self.match
                                    else:
                                        self.match.append(
                                            'match-dates--confidence=0--The dates do not match (' + str(self.dates1) + ' and ' + str(d) +'). These are not likely to be the same person.--')
                                        self.overallconfidence = 0
                                        return self.match

                            else:
                                self.match.append(
                                    'match-dates--confidence=0--We only have one date (' + str(self.dates1) + ') and nothing to compare it to.--')
                                return self.match

                        # otherwise we have two dates, test them
                        else:
                            for dt in self.dates1:
                                for d in self.dates2:
                                    if dt == d:
                                        self.match.append('match-dates--confidence=' + str(
                                            1.0) + '--There is an exact match with birth and death dates (' + str(self.dates1) + ' and ' + str(self.dates2) + '). These are very likely the same person.--')
                                        self.overallconfidence = 1.0
                                        return self.match
                                    else:
                                        self.match.append('match-dates--confidence=' + str(
                                            0) + '--The dates do not match (' + str(self.dates1) + ' and ' + str(self.dates2) + '). These are not likely to be the same person.--')
                                        self.overallconfidence = 0
                                        return self.match
                # if we don't have a name one or both there's not much more we can do
                else:
                    if not names1 and not names2:
                        self.match.append('match-name--There are no names specified--')
                    elif not names1:
                        self.match.append('match-name--There is no name for ' + self.value1label + ' (' + self.value1 + ')--')
                    elif not names2:
                        self.match.append('match-name--There is no name for ' + self.value2label + ' (' + self.value2 + ')--')

                    return self.match

        else:
            count = self.listcount - 1
            if count < 2:
                self.match.append('match--insufficient items in the list count=' + str(count))
            return self.match

    # similar to the first pass but concentrates on checking external resources
    def secondpass(self, value, external=None):

        if self.sameas(value, external=external):
            results = self.sameas(value, select=True, external=external)

            if results:
                self.match.append("sameas-external--There are sameas links in " + value + "--")

                if external:
                    try:
                        for res in results["results"]["bindings"]:
                            dates = self.checkdates(res["o"]["value"], secondpass=True)
                            if dates:
                                self.match.append("match-dates-external--dates found in " + res["o"][
                                    "value"] + ". Check if they match.--")
                                return dates
                    except Exception as e:
                        logger.error('ERROR same_person.py - ' + e.message + ' (secondpass1)')
                        return []
                else:
                    for res in results:
                        try:
                            dates = self.checkdates(res.getValue('o').getValue(), secondpass=True)
                            if len(dates) > 0:
                                self.match.append("match-dates-external--dates found in " + res.getValue('o').getValue() + ". Check if they match.--")

                                return dates

                            else:
                                self.match.append(
                                    "match-dates-external--no dates available in " + res.getValue(
                                        'o').getValue() + "--")
                                dates = self.secondpass(res.getValue('o').getValue(), external=True)
                                return dates

                        except Exception as e:
                            logger.error('ERROR same_person.py - ' + e.message + ' (secondpass2)')

            else:
                self.match.append("sameas-external--There are no sameas links for " + value + "--")

    # check for sameas links, the implementation differs if we are querying the local private tmp reopsitory or an external graph
    def sameas(self, value1, value2='?o', select=False, external=None):
        conn = connect.Connect('tmp', cat='private-catalog')

        if select and not external:
            results = sparql_query_private.QueryPrivate(conn.repoconn(), 'select ?o { <' + value1 +
                '> <http://www.w3.org/2002/07/owl#sameas> ?o }', ).query()
            return results

        # if the resource is external RDF, fetch it
        if external:
            results = process_rdf.ProcessRdf().fromuri(value1).query(
                'select ?o { { <' + value1 + '> <http://www.w3.org/2002/07/owl#sameas> ?o . ?s ?p ?o } UNION { <' +
                value1 + '> <http://www.w3.org/2002/07/owl#sameAs> ?o . ?s ?p ?o } }')
            jsonres = json.loads(results.serialize(format="json"))

            return jsonres

        if value2 == '?o':
            if sparql_query_private.QueryPrivate(conn.repoconn(), 'ask '
                    '{ { <' + value1 + '> <http://www.w3.org/2002/07/owl#sameas> ?o } UNION '
                    '{ ?o <http://www.w3.org/2002/07/owl#sameas> <' + value1 + '> } } '
                    '',query='ask').query():
                conn.close()
                return True
            else:
                conn.close()
                return False

        else:

            if sparql_query_private.QueryPrivate(conn.repoconn(), 'ask '
                    '{ { <' + value1 + '> <http://www.w3.org/2002/07/owl#sameas> <' + value2 + '> } UNION '
                    '{ <' + value2 + '> <http://www.w3.org/2002/07/owl#sameas> <' + value1 + '> } UNION '
                    '{ <' + value2 + '> <http://dbpedia.org/ontology/wikiPageRedirects> <' + value1 + '> } UNION '
                    '{ <' + value1 + '> <http://dbpedia.org/ontology/wikiPageRedirects> <' + value2 + '> }  } '
                    '', query='ask').query():
                conn.close()
                return True
            elif sparql_query_private.QueryPrivate(conn.repoconn(),
                                            'ask { <' + value2 + '> <http://www.w3.org/2002/07/owl#sameas> <' + value1 + '> }',
                                            query='ask').query():
                conn.close()
                return True
            else:
                conn.close()
                return False

    # check the names
    def checkname(self, value, num):

        conn = connect.Connect('tmp', cat='private-catalog')
        results = sparql_query_private.QueryPrivate(conn.repoconn(), 'SELECT ?o ?u { { <' + value + '> <http://xmlns.com/foaf/0.1/name> ?o . BIND (isURI(?o) as ?u) } UNION { <' + value + '> <http://erlangen-crm.org/current/P1_is_identified_by> ?o . BIND (isURI(?o) as ?u) } UNION { <' + value + '> <http://dlib.york.ac.uk/ontologies/vocupper#hasName> ?o . BIND (isURI(?o) as ?u) } }').query()
        conn.close()

        names = []

        if results:
            for res in results:
                try:
                    if res.getValue('u').getValue() == 'true':
                        results = process_rdf.ProcessRdf().fromuri(res.getValue('o').getValue()).query(
                            'SELECT DISTINCT ?s ?p ?o WHERE { { ?s <http://www.w3.org/2000/01/rdf-schema#label> '
                            '?o . ?s ?p ?o } UNION { ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?o . ?s ?p ?o } }')

                        jsonres = json.loads(results.serialize(format="json"))

                        for res in jsonres["results"]["bindings"]:

                            if res["o"]["value"] not in names:
                                names.append(res["o"]["value"])

                            #let's store this data
                            if self.contexts:
                                add = add_triple.AddTriple(conn.repoconn())
                                add.setcontexts(self.contexts)
                                add.setupsubject(res["s"]["value"])
                                add.adduri(res["p"]["value"], res["o"]["value"])

                                conn.repoconn().deleteDuplicates('spo')
                    else:
                        names.append(res.getValue('o').getValue())
                except Exception as e:
                    logger.error('ERROR same_person.py - ' + e.message + ' (checkname)')

        else:

            conn = connect.Connect('tmp', cat='private-catalog')
            results = sparql_query_private.QueryPrivate(conn.repoconn(), 'SELECT ?o { <' + value + '> <http://dbpedia.org/ontology/wikiPageRedirects> ?o}').query()
            conn.close()

            for res in results:
                if res.getValue('o') is None:
                    print 'do nothing'
                else:
                    graph = process_rdf.ProcessRdf().fromuri(res.getValue('o').getValue())
                    jsonres = json.loads(graph.query(
                        'SELECT ?o { { <' + res.getValue('o').getValue() + '> <http://xmlns.com/foaf/0.1/name> ?o } UNION { <' + res.getValue('o').getValue() + '> <http://erlangen-crm.org/current/P1_is_identified_by> ?o } UNION { <' + res.getValue('o').getValue() + '> <http://dlib.york.ac.uk/ontologies/vocupper#hasName> ?o } }').serialize(format="json"))

                    for r in jsonres["results"]["bindings"]:
                        names.append(r["o"]["value"])

                if jsonres:
                    if self.contexts:
                        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
                        #let's add the data retrieved
                        addnew = add_triple.AddTriple(conn)
                        addnew.setcontexts(self.contexts)
                        addnew.setupsubject(res.getValue('o').getValue())

                        jsonr = json.loads(graph.query(
                            'SELECT * { <' + res.getValue('o').getValue() + '> ?p ?o . FILTER (isLiteral(?o)) }').serialize(format="json"))

                        for r in jsonr["results"]["bindings"]:
                            addnew.addliteral(r["p"]["value"], r["o"]["value"])

                        jsonr = json.loads(graph.query(
                            'SELECT * { <' + res.getValue('o').getValue() + '> ?p ?o . FILTER (isURI(?o)) }').serialize(format="json"))

                        for r in jsonr["results"]["bindings"]:
                            addnew.adduri(r["p"]["value"], r["o"]["value"])
                    conn.deleteDuplicates('spo')
                    conn.close()

                    if num == 1:
                        self.match.append('match-name--Redirect found for ' + self.value1 + ' changing URI to ' + res.getValue('o').getValue())
                        self.value1 = res.getValue('o').getValue()

                    elif num == 2:
                        self.match.append('match-name--Redirect found for ' + self.value1 + ' changing URI to ' + res.getValue('o').getValue())
                        self.value2 = res.getValue('o').getValue()

        return names

    # get the dates vor the supplied value, if secondpass, this indicates we're retrieving rdf
    def checkdates(self, value, secondpass=None):

        querystring = 'SELECT ?b ?d ?u { { OPTIONAL { <' + value + '> <http://erlangen-crm.org/current/P100_died_in> ?d . }<' + value + '> <http://erlangen-crm.org/current/P98i_was_born> ?b . BIND (isURI(?b) as ?u) } UNION { OPTIONAL { <' + value + '> <http://data.archiveshub.ac.uk/def/dateDeath> ?d . } <' + value + '> <http://data.archiveshub.ac.uk/def/dateBirth> ?b . BIND (isURI(?b) as ?u) } UNION { OPTIONAL { <' + value + '> <http://dbpedia.org/property/dateOfDeath> ?d . } <' + value + '> <http://dbpedia.org/property/dateOfBirth> ?b . BIND (isURI(?b) as ?u) } UNION { OPTIONAL { <' + value + '> <http://dbpedia.org/ontology/deathDate> ?d . } <' + value + '> <http://dbpedia.org/ontology/birthDate> ?b . BIND (isURI(?b) as ?u) } UNION { OPTIONAL { <' + value + '> <http://yago-knowledge.org/resource/diedOnDate> ?d . }<' + value + '> <http://yago-knowledge.org/resource/wasBornOnDate> ?b . BIND (isURI(?b) as ?u) } UNION { <' + value + '> <http://rdvocab.info/ElementsGr2/dateOfDeath> ?d . <' + value + '> <http://rdvocab.info/ElementsGr2/dateOfBirth> ?b . BIND (isURI(?b) as ?u) } }'
        dates = []
        results = []
        secondpassresults = []

        if secondpass:
            try:
                secondpassresults = json.loads(process_rdf.ProcessRdf().fromuri(value).query(querystring).serialize(
                    format="json"))

            except Exception as e:
                logger.error('ERROR same_person.py - ' + e.message + ' (checkdates1)')

        else:
            conn = connect.Connect('tmp', cat='private-catalog')
            results = sparql_query_private.QueryPrivate(conn.repoconn(), querystring).query()
            conn.close()

        if results:
            for res in results:
                if res.getValue('u') is None:
                    dates = []
                elif res.getValue('u').getValue() == 'true':
                    try:
                        g1 = process_rdf.ProcessRdf().fromuri(res.getValue('b').getValue())
                        g2 = process_rdf.ProcessRdf().fromuri(res.getValue('d').getValue())
                        graph = g1 + g2

                        jsonres = json.loads(graph.query(
                            'SELECT DISTINCT ?s ?p ?o ?u WHERE { { ?s ?p ?o . BIND (isURI(?o) as ?u) } MINUS { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o} MINUS { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?o } } ORDER BY ?o').serialize(
                            format="json"))

                        graphtwo = ConjunctiveGraph()
                        birth = None
                        death = None
                        count = 1

                        for res in jsonres["results"]["bindings"]:
                            if res["u"]["value"]:
                                if graphtwo:
                                    graphtwo += process_rdf.ProcessRdf().fromuri(res["o"]["value"])
                                else:
                                    graphtwo = process_rdf.ProcessRdf().fromuri(res["o"]["value"])

                                jsonr = json.loads(graphtwo.query(
                                    'SELECT DISTINCT ?s ?p ?o ?u WHERE { ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o . BIND (isURI(?o) as ?u) } ORDER BY ?o').serialize(
                                    format="json"))

                                for r in jsonr["results"]["bindings"]:

                                    conn = connect.Connect('tmp', cat='private-catalog')
                                    add = add_triple.AddTriple(conn.repoconn())
                                    add.setcontexts(self.contexts)
                                    add.setupsubject(r["s"]["value"])

                                    if count == 1:

                                        birth = r["o"]["value"]
                                        if self.contexts:
                                            add.addrdflabel(birth)
                                    elif count == 2:

                                        death = r["o"]["value"]
                                        if self.contexts:
                                            add.addrdflabel(death)
                                    count += 1

                                    conn.repoconn().deleteDuplicates('spo')
                                    conn.close()

                                count = 1  # reset count

                            elif 'http://www.w3.org/2000/01/rdf-schema#label' in res["p"]["value"]:
                                conn = connect.Connect('tmp', cat='private-catalog')
                                add = add_triple.AddTriple(conn.repoconn())
                                add.setcontexts(self.contexts)
                                add.setupsubject(res["s"]["value"])

                                if count == 1:
                                    birth = res["o"]["value"]
                                    if self.contexts:
                                        add.addrdflabel(birth)
                                elif count == 2:
                                    death = res["o"]["value"]
                                    if self.contexts:
                                        add.addrdflabel(death)
                                count += 1

                                conn.repoconn().deleteDuplicates('spo')
                                conn.close()

                        # let's add the birth/death dates if we have them
                        if birth:
                            birthparts = birth.split('-')
                            deathparts = death.split('-')
                            for part in birthparts:
                                if len(part) == 4:
                                    birth = part
                            for part in deathparts:
                                if len(part) == 4:
                                    death = part
                            dates.append(birth + '-' + death)

                        return dates

                    except Exception as e:
                        logger.error(
                            'ERROR same_person.py - ' + e.message + ' (checkdates - res.getValue(u) if true loop')

                elif res.getValue('u').getValue() == 'false':
                    try:
                        birthparts = res.getValue('b').getValue().split('-')
                        deathparts = res.getValue('d').getValue().split('-')
                        for part in birthparts:
                            if len(part) == 4:
                                birth = part
                            for part in deathparts:
                                if len(part) == 4:
                                    death = part
                        dates.append(birth + '-' + death)

                        return dates

                    except Exception as e:
                        logger.error('ERROR same_person.py - ' + e.message + ' (checkdates - res.getValue(u) else loop')

        if secondpassresults:
            for res in secondpassresults["results"]["bindings"]:
                if res["u"]["value"] == 'true':
                    g1 = process_rdf.ProcessRdf().fromuri(res["b"]["value"])
                    g2 = process_rdf.ProcessRdf().fromuri(res["d"]["value"])
                    graph = g1 + g2

                    jsonres = json.loads(graph.query(
                        'SELECT DISTINCT ?s ?p ?o ?u WHERE { { ?s ?p ?o . BIND (isURI(?o) as ?u) } MINUS { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o} MINUS { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?o } } ORDER BY ?o').serialize(
                        format="json"))

                    graph = ConjunctiveGraph()
                    birth = None
                    death = None
                    count = 1
                    for res in jsonres["results"]["bindings"]:
                        if res["u"]["value"]:
                            graph = graph + process_rdf.ProcessRdf().fromuri(res["o"]["value"])

                        elif 'http://www.w3.org/2000/01/rdf-schema#label' in res["p"]["value"]:
                            conn = connect.Connect('tmp', cat='private-catalog')
                            add = add_triple.AddTriple(conn.repoconn())
                            add.setcontexts(self.contexts)
                            add.setupsubject(r["s"]["value"])

                            if count == 1:
                                birth = res["o"]["value"]
                                if self.contexts:
                                    add.addrdflabel(birth)
                            elif count == 2:
                                death = res["o"]["value"]
                                if self.contexts:
                                    add.addrdflabel(death)
                            count += 1

                            conn.repoconn().deleteDuplicates('spo')
                            conn.close()
                    count = 1
                    if birth:
                        birthparts = birth.split('-')
                        deathparts = death.split('-')
                        dates.append(birthparts[0] + '-' + deathparts[0])

                    jsonres = json.loads(graph.query(
                        'SELECT DISTINCT ?s ?p ?o ?u WHERE { ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o . BIND (isURI(?o) as ?u) } ORDER BY ?o').serialize(
                        format="json"))

                    for res in jsonres["results"]["bindings"]:
                        if count == 1 and len(str(res["o"]["value"])) >= 4:
                            birth = res["o"]["value"]
                            count += 1
                        elif count == 2 and len(str(res["o"]["value"])) >= 4:
                            death = res["o"]["value"]
                            count += 1
                    birthparts = birth.split('-')
                    deathparts = death.split('-')
                    for part in birthparts:
                        if len(part) == 4:
                            birth = part
                    for part in deathparts:
                        if len(part) == 4:
                            death = part
                    dates.append(birth + '-' + death)

                elif res["u"]["value"] == 'false':
                    birthparts = res["b"]["value"].split('-')
                    deathparts = res["d"]["value"].split('-')
                    for part in birthparts:
                        if len(part) == 4:
                            birth = part
                    for part in deathparts:
                        if len(part) == 4:
                            death = part
                    dates.append(birth + '-' + death)

            return dates

    def getconfidence(self):
        return self.overallconfidence