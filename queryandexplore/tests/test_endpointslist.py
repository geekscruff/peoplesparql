__author__ = 'geekscruff'

from unittest import TestCase
from queryandexplore import endpoints_list
from queryandexplore import endpoint

class TestEndpoint(TestCase):
    def test_endpointslist(self):
        # first make sure the endpoint is in the list
        endpoint.Endpoint('http://collection.britishmuseum.org/sparql').setup_existing_sparql_endpoint()
        # then get the list
        results = str(endpoints_list.EndpointsList().listall('test'))
        self.assertIn("http://collection.britishmuseum.org/sparql", results)
