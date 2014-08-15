__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import same_person

class TestSamePerson(TestCase):
    def test_sameas(self):
        #Martin Maingaud
        list = [{u'head': {u'vars': [u's', u'o']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://collection.britishmuseum.org/id/person-institution/36897'}, u'o': {u'type': u'literal', u'value': u'Martin Maingaud'}}]}}, {u'head': {u'vars': [u'o', u's']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://dlib.york.ac.uk/id/person/35403'}, u'o': {u'type': u'literal', u'value': u'Maingaud, Martin (active 1692-1724); painter; Nationality: French'}}]}}]
        #Peter Lely
        #list = [{u'head': {u'vars': [u's', u'o']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://collection.britishmuseum.org/id/person-institution/35418'}, u'o': {u'type': u'literal', u'value': u'Sir Peter Lely'}}]}}, {u'head': {u'vars': [u'o', u's']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://dlib.york.ac.uk/id/person/34385'}, u'o': {u'type': u'literal', u'value': u'Lely, Sir Peter (1618-80); owner of prints/drawings; painter; seller of pictures; Nationality: Dutch'}}]}}]
        #Charles Darwin
        #list = [{u'head': {u'vars': [u's', u'o']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://data.archiveshub.ac.uk/id/person/gb738/darwincharles1809-1882naturalist'}, u'o': {u'xml:lang': u'EN', u'type': u'literal', u'value': u'Darwin, Charles, 1809-1882, naturalist'}}]}}, {u'head': {u'vars': [u's', u'o']}, u'results': {u'bindings': [{u's': {u'type': u'uri', u'value': u'http://collection.britishmuseum.org/id/person-institution/122654'}, u'o': {u'type': u'literal', u'value': u'Charles Darwin'}}]}}]
        sp = same_person.SamePerson(list, context='<http://geekscruff.me/tmp#testuser@example.com>')
        result = sp.first_pass()
        #print result
        for res in result:
            print res