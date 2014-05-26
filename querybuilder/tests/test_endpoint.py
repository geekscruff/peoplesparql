__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import endpoint
from datawrangler import connect

class TestEndpoint(TestCase):
    def setUp(self):
        conn = connect.Connect('test')
        #conn.deletetestdata()
        conn.close()

    # def test_new_endpoint(self):
    #     ep = endpoint.Endpoint('http://data.archiveshub.ac.uk/sparql')
    #     ep.setup_new_sparql_endpoint('The Archives Hub')
    #     self.assertIn("http://data.archiveshub.ac.uk/sparql", str(ep.getdetails()))
    #
    def test_existing_endpoint(self):
        ep = endpoint.Endpoint('http://collection.britishmuseum.org/sparql').setup_existing_sparql_endpoint()
        self.assertIn("http://collection.britishmuseum.org/sparql", str(ep.getdetails()))
