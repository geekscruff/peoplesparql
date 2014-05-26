__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import endpoint_creator
from datawrangler import connect


class TestEndpointCreator(TestCase):
    def createep(self, ep):
        conn = connect.Connect('test')
        conn.deletetestdata()
        conn.close()
        r = endpoint_creator.EndpointCreator(ep, 'test', 'Archives Hub')
        self.ep = ep
        return r

    def test_setup_11(self):
        r = self.createep('http://data.archiveshub.ac.uk/sparql')
        results = r.docreate()
        self.assertIn('http://data.archiveshub.ac.uk/sparql', str.lower(str(results)))

    def test_setup_10(self):
        r = self.createep('http://bnb.data.bl.uk/sparql')
        results = r.docreate()
        self.assertIn('http://bnb.data.bl.uk/sparql', str.lower(str(results)))



