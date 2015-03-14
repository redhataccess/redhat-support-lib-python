'''
Created on Apr 10, 2012

@author: Keith Robertson
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
from redhat_support_lib.xml import params
import ConfigParser
import unittest
import os
import logging

__author__ = 'Keith Robertson <kroberts@redhat.com>'

class articleTest(unittest.TestCase):

    def setUp(self):
        print ""
        print "*********************************************************************"
        print "*********************************************************************"
        print "*********************************************************************"
        self.config = ConfigParser.ConfigParser()
        self.config.read('strata.cfg')
        self.user = self.config.get('strata', 'internal_username')
        if (self.user.startswith('$')):
            self.user = os.environ.get(self.user[1:])
            print "Username: ", self.user
            logging.log(logging.DEBUG, "Username: %s" % self.user)

        self.passwd = self.config.get('strata', 'internal_password')
        if (self.passwd.startswith('$')):
            self.passwd = os.environ.get(self.passwd[1:])
            logging.log(5, "password: %s" % self.passwd)

        self.url = self.config.get('strata', 'url')
        if (self.url.startswith('$')):
            self.url = os.environ.get(self.url[1:])
            print "url: ", self.url

        self.api = API(username=self.user,
                       password=self.passwd,
                       url=self.url,
                       no_verify_ssl=True)


    def tearDown(self):
        self.api.disconnect()


    def testAddGetUpdateArticle(self):
        print " *******  testAddGetUpdateArticle *******"
        try:
            print "Create a new article object..."
            art = self.api.im.makeArticle(createdBy='rhn-support-cbredese',
                                          title='Pyunit REST API TC for Articles',
                                          summary="Summary text here",
                                          kcsState='wip',
                                          body='Body text here')

            self.assertNotEqual(art, None)

            print "which looks like this:"
            print art.toXml()

            print "===================================================="
            print "Add the article via strata..."
            doc = self.api.articles.add(art)

            self.assertNotEqual(doc, None)
            self.assert_(doc.get_id() is not None, doc)

            print "===================================================="
            print "Get the article we just created..."
            art = self.api.articles.get(doc.id)

            self.assertNotEqual(art, None)

            print "----------------------------------------------------"
            print "which looks like this:"
            print art.toXml()

            print "===================================================="
            print "Update the article..."

            new_text = 'Updated resolution text'
            art.set_body(new_text)

            print "WHich now looks like this:"
            print art.toXml()

            self.assertEqual(art.get_body(), new_text)
            art.update()

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")
        pass


    def testGetArticle(self):
        print "---testGetArticle---"
        sid = self.config.get('testGetArticle', 'artID')
        print "Getting article %s" % sid
        try:
            art = self.api.articles.get(sid)
            print art
            self.assert_(art is not None, art)
            print "Article title(%s)" % art.get_title()
            self.assertEqual(art.get_title(), self.config.get('testGetArticle', 'title'))
            print "Article authorSSOName(%s)" % art.get_authorSSOName()
            self.assertEqual(art.get_authorSSOName(), self.config.get('testGetArticle', 'authorSSOName'))
        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")


    # this is blocked by BZ866726 (https://bugzilla.redhat.com/show_bug.cgi?id=866726)
    def testFilterArticles(self):
        print "---testFilterArticles---"
        print "This test case is blocked by BZ866726 (https://bugzilla.redhat.com/show_bug.cgi?id=866726)"
        return

        try:
            artAry = self.api.articles.list(self.config.get('testFilterArticles', 'keyword'),
                                            title=self.config.get('testFilterArticles', 'title'))
            self.assert_(artAry is not None and len(artAry) > 0, artAry)
            for art in artAry:
                print "Found the following article:"
                print art.toXml()

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")
        pass


    def testArticleElements(self):
        print "---Testing various article attributes---"
        try:
            art = self.api.im.makeArticle()

            # required fields
            art.set_kcsState('wip')
            art.set_title('strata API test')

            # deprecated / duplicate fields
            art.add_tag('tags 1')
            art.add_tag('tags 2')

            body = params.articleBodyType('Article Body')
            art.set_articleBody(body)

            # optional but sensitive
            art.set_language('en')

            # optional fields
            art.set_uidName('UID Name')
            art.set_issue('issue')
            art.set_environment('environment')
            art.set_resolution('resolution')
            art.set_rootCause('root cause')
            art.set_internalDiagnosticSteps('Internal Diagnostic Steps...')
            art.set_externalDiagnosticSteps('External Diagnostic Steps...')
            art.set_summary('Summary')
            art.add_case(('http://mycompany.com/caseURI-1'))
            art.add_case(('http://mycompany.com/caseURI-2'))
            art.add_tag('tag 1')
            art.add_tag('tag 2')
            art.set_published('false')
            art.add_duplicateOf('12345')
            art.add_duplicateOf('67890')
            art.set_explanation('Article Explanation')
            art.set_body('article body')

            print art.toXml()

            print "--- creating article ---"
            doc = self.api.articles.add(art)
            print "\n----------------\n"
            print doc.toXml()
        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")
        pass


if __name__ == "__main__":

    # Do something clever with the command line nuggets
    use = "Usage: %prog [options] [test_case test_case ...]"
    parser = OptionParser(usage=use)

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Disable verbose debug output")
    parser.add_option("-l", "--list", dest="list", action="store_true", default=False, help="List all test cases")
    options, args = parser.parse_args()

    # enable logging, as needed
    if options.quiet == False:
        logging.basicConfig(level=logging.DEBUG)

    # get testcase list
    cases = unittest.defaultTestLoader.getTestCaseNames(articleTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(articleTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
