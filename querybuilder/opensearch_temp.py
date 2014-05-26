__author__ = 'geekscruff'

import httplib
import requests

# This is just a test file

r = requests.get("http://viaf.org/viaf/search?query=cql.any+all%22dempsey%22", headers={"Accept": "application/rss+xml"})

print r
