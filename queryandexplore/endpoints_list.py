__author__ = 'geekscruff'

"""Return a list of all endpoints in the local datastores repository, two methods,
return all (name and uri) or just return uris"""

from queryandexplore import sparql_select
from datawrangler import connect
import logging

logger = logging.getLogger(__name__)

class EndpointsList():
    def __init__(self):
        logger.debug("DEBUG endpoints_list.py - object instantiated")

    def listall(self, repo):
        conn = connect.Connect(repo)
        conn.repoconn()
        val = "?s <http://dublincore.org/documents/dcmi-terms/#elements-title> ?o"
        sel = sparql_select.SparqlSelect(val, conn.repourl(), sel='?s ?o', dist=True, order="?o")
        conn.close()
        logger.debug("DEBUG endpoints_list.py - return all names and uris")
        return sel.select()

    def listalluris(self, repo):
        conn = connect.Connect(repo)
        conn.repoconn()
        val = "?s <http://dublincore.org/documents/dcmi-terms/#elements-title> ?o"
        sel = sparql_select.SparqlSelect(val, conn.repourl(), sel='?s', dist=True)
        conn.close()
        logger.debug("DEBUG endpoints_list.py - return all uris")
        return sel.select()
