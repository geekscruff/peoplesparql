__author__ = 'geekscruff'

from querybuilder import sparql_select
from datawrangler import connect
import logging

logger = logging.getLogger(__name__)

# Return a list of all endpoints in the local datastores repository, two methods,
# return all (name and uri) or just return uris


class EndpointsList():
    def __init__(self):
        logger.debug("DEBUG endpointslist.py - object instantiated")

    def listall(self, repo):
        conn = connect.Connect(repo)
        conn.repoconn()
        val = "?s <http://dublincore.org/documents/dcmi-terms/#elements-title> ?o"
        sel = sparql_select.SparqlSelect(val, conn.repourl(), 0, '?s ?o')
        sel.distinct()
        conn.close()
        logger.debug("DEBUG endpointslist.py - return all names and uris")
        return sel.select()

    def listalluris(self, repo):
        conn = connect.Connect(repo)
        conn.repoconn()
        val = "?s <http://dublincore.org/documents/dcmi-terms/#elements-title> ?o"
        sel = sparql_select.SparqlSelect(val, conn.repourl(), 0, '?s')
        sel.distinct()
        conn.close()
        logger.debug("DEBUG endpointslist.py - return all uris")
        return sel.select()
