__author__ = 'geekscruff'

import logging
from datawrangler import query_private

logger = logging.getLogger(__name__)

# Handles deleting all triples from the repository, either from a context or the whole repository.
# It would be easy to extend this to individual triples with removeTriple().


class DeleteTriples():
    def __init__(self, conn):  # conn is the repository connection
        logger.debug('DEBUG addtriple.py - object instantiated')
        self.conn = conn
        self.contexts = []


    def delete_all(self, context=None):
        if context:
            self.conn.clear(context)
        else:
            self.conn.clear()




