__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import addtriple, connect

def tryconnect():
    testconnect = connect.Connect('test1').repoconn()
    return testconnect

def tryadd(tc):
    testadd = addtriple.AddTriple(tc)
    testadd.setupsubject('http://dbpedia.org/void/Dataset')
    testadd.adduri('http://geekscruff.me/ns/dataset#typeForPersonalName', 'http://xmlns.com/foaf/0.1/Person')
    testadd.addliteral('http://xmlns.com/foaf/0.1/name', 'Some Name')
    testadd.addrdflabel('Some Label')
    testadd.addrdftype('http://rdfs.org/ns/void#Dataset')

class TestAdd(TestCase):
    def test_add_triples(self):
        tc = tryconnect()
        size = tc.size()
        tryadd(tc)
        self.assertEqual(size + 4, tc.size())

    def test_add_triples_error(self):
        tc = tryconnect()
        size = tc.size()
        testadd = addtriple.AddTriple(tc)
        testadd.setupsubject('http://dbpedia.org/void/Dataset')
        testadd.adduri('geekscruff.me/ns/dataset#typeForPersonalName', 'dafghgxmlns.com/foaf/0.1/Person')
        self.assertEqual(size, tc.size())

    def test_add_triples_context(self):
        tc = tryconnect()
        size = tc.size()
        testadd = addtriple.AddTriple(tc)
        contexts = '<http://geekscruff.me/context1>'
        testadd.setcontexts(contexts)
        testadd.setupsubject('http://geekscruff.me/Dataset')
        testadd.addliteral('http://geekscruff.me/ns/dataset#typeForPersonalName', 'bumface')

        self.assertEqual(size + 1, tc.size())

