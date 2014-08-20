__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import connect
from queryandexplore import sparql_query_private


class TestQueryPrivate(TestCase):
    def test_query_private_select(self):
        querystring = "SELECT ?s ?p ?o FROM <http://geekscruff.me/tmp#permanentdata> WHERE { ?s ?p ?o }"
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
        result = sparql_query_private.QueryPrivate(conn, querystring).query()

        self.assertEquals(result.rowCount(), 61)


