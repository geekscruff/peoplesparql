__author__ = 'geekscruff'

from unittest import TestCase
from queryandexplore import process_rdf

class TestProcessRdf(TestCase):

    def test_load_rdf(self):

        subs = ''

        try:
            g = process_rdf.ProcessRdf().fromuri('http://viaf.org/viaf/7657501/rdf')

            for s,p,o in g:
                subs += s

        except Exception as e:
            print(e.message)

        self.assertIn('http://viaf.org/viaf/7657501', subs)


    def test_parse_rdf(self):

        subs = ''

        try:
            g = process_rdf.ProcessRdf().fromuri2('http://viaf.org/viaf/7657501/rdf')

            for s,p,o in g:
                subs += s

        except Exception as e:
            print(e.message)

        self.assertIn('http://viaf.org/viaf/7657501', subs)
