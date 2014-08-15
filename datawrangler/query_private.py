__author__ = 'geekscruff'

import logging
from franz.openrdf.repository.repository import Repository # this is needed
from franz.openrdf.query.query import QueryLanguage
from datawrangler import connect

logger = logging.getLogger(__name__)

# Use the agraph python library to query in private repositories
# For public queries use the querybuilder module

class QueryPrivate():
    def __init__(self, conn, querystring, query='select'):  # Supply the repository name and the context
        if query == 'select':
            logger.info('INFO -- query_private.py -- setting up SELECT query for ' + querystring)
            self.tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, querystring)
        elif query == 'ask':
            logger.info('INFO -- query_private.py -- setting up ASK query for ' + querystring)
            self.tupleQuery = conn.prepareBooleanQuery(QueryLanguage.SPARQL, querystring)
    def query(self):
        logger.info('INFO -- query_private.py -- evaluating query')
        return self.tupleQuery.evaluate()
