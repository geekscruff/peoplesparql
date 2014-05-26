__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import endpointslist

class TestEndpoint(TestCase):
    def test_endpointslist(self):
        results = str(endpointslist.EndpointsList().listall('test'))
        self.assertIn("http://collection.britishmuseum.org/sparql", results)
