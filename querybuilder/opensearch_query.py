__author__ = 'geekscruff'

from opensearch import Client
import logging
logger = logging.getLogger(__name__)

# This is just a test class at the moment


class OpensearchQuery:
    def __init__(self):
        logger.debug("Instantiate opensearch query object")
        self.tryaquery()

    def tryaquery(self):
        print("dunno")
        client = Client('http://geekscruff.me/opensearch/VIAFallFieldsSearch.xml')
        results = client.search("jane austen")

        for result in results:
            print result.title, result.link


