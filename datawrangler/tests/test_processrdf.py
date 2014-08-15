__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import processrdf
import json

class TestProcessRdf(TestCase):

    def test_load_rdf(self):

        subs = ''

        try:
            g = processrdf.ProcessRdf().fromuri('http://viaf.org/viaf/7657501/rdf')

            for s,p,o in g:
                subs += s

            rr = g.query('SELECT * {?s ?p ?o}')

            j = json.loads(rr.serialize(format="json"))

            #for res in j["results"]["bindings"]:
                #print res["s"]["value"]
                #print res["p"]["value"]
                #print res["o"]["value"]

        except Exception as e:
            print(e.message)

        self.assertIn('http://viaf.org/viaf/7657501', subs)


    def test_parse_rdf(self):

        try:
            g = processrdf.ProcessRdf().fromuri2('http://viaf.org/viaf/7657501/rdf')

            rr = g.query('SELECT * {?s ?p ?o}')

            j = json.loads(rr.serialize(format="json"))

            for res in j["results"]["bindings"]:
                print res["s"]["value"]
                print res["p"]["value"]
                print res["o"]["value"]

        except Exception as e:
            print(e.message)
