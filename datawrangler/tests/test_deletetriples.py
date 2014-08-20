__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import delete_triples, connect

class TestQueryPrivate(TestCase):

    def test_delete_triples(self):
        conn = connect.Connect('test', cat='public-catalog').repoconn()
        delete_triples.DeleteTriples(conn).delete_all()
        self.assertEquals(conn.size(), 0)
        conn.close()