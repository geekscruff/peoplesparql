__author__ = 'geekscruff'

from unittest import TestCase
from datawrangler import connect

def tryconn():
    testconnect = connect.Connect('test')
    return testconnect

class TestConnect(TestCase):
    def test_connect_name(self):
        conn = tryconn()
        self.assertEqual(conn.reponame(), 'test')
        conn.close()

    def test_connect_url(self):
        conn = tryconn()
        self.assertEqual(conn.repourl(), 'http://geekscruff.me:10035/catalogs/public-catalog/repositories/test')
        conn.close()

    def test_connect_size(self):
        conn = tryconn()
        self.assertEqual(conn.repoconn().size(), 0)
        conn.close()

    def test_delete_test(self):
        conn = tryconn()
        conn.deletetestdata()
        self.assertEqual(conn.repoconn().size(), 0)
        conn.close()