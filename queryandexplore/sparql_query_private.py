__author__ = 'geekscruff'

"""Use the agraph python library to query in private repositories of allegrograph
For public queries use the sparql_ask and sparql_select or sparql_query_specific classes"""

import logging
from franz.openrdf.repository.repository import Repository # this is needed
from franz.openrdf.query.query import QueryLanguage

logger = logging.getLogger(__name__)

# TODO re-factor to use the same classes as a non-private query

class QueryPrivate():
    def __init__(self, conn, querystring, query='select'):  # Supply the repository name and the context
        if query == 'select':
            logger.info('INFO -- sparql_query_private.py -- setting up SELECT query for ' + querystring)
            #prepare the query
            self.tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, querystring)
        elif query == 'ask':
            logger.info('INFO -- sparql_query_private.py -- setting up ASK query for ' + querystring)
            #prepare the query
            self.tupleQuery = conn.prepareBooleanQuery(QueryLanguage.SPARQL, querystring)

    def query(self):
        # perform the query
        logger.info('INFO -- sparql_query_private.py -- evaluating query')
        return self.tupleQuery.evaluate()
