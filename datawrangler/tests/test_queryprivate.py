__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import query_private, connect

class TestQueryPrivate(TestCase):
    def test_query_private_select(self):
        querystring = "SELECT ?s ?p ?o FROM <http://geekscruff.me/tmp#j.allinson@gmail.com> WHERE { ?s ?p ?o }"
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
        result = query_private.QueryPrivate(conn, querystring).query()

        for res in result:
            print(type(res.getValue('o').getValue()))

        self.assertEquals(result.rowCount(), 1)

    # unsupported
    def test_query_private_delete(self):
        querystring = "WITH <http://geekscruff.me/tmp#testuser@example.com> DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }"
        conn = connect.Connect('tmp', cat='private-catalog').repoconn()
        result = query_private.QueryPrivate(conn, querystring).query()

        self.assertEquals(result.rowCount(), 1)


