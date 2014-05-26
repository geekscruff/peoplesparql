__author__ = 'geekscruff'

from unittest import TestCase


def switch(x):
    return {
        1: 'http://xmlns.com/foaf/0.1/Person',
        2: 'http://dbpedia.org/ontology/Person',
        3: 'http://erlangen-crm.org/current/E21_Person',
    }.get(x, 1)  # 1 is default if x not found


class TestConnect(TestCase):
    def test_connect_name(self):
        self.assertEqual(switch(1), 'http://xmlns.com/foaf/0.1/Person')