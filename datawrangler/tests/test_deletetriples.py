__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import delete_triples, connect

class TestQueryPrivate(TestCase):

    # doesn't work
    def test_delete_triples(self):
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
        delete_triples.DeleteTriples(conn).delete_all('<http://geekscruff.me/tmp#testuser@example.com>')
        self.assertEquals(conn.size(), 0)
        conn.close()