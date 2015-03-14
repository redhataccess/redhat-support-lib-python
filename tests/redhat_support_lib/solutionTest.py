'''
Created on Apr 10, 2012

@author: Keith Robertson
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.brokers import solutions, solution
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
import ConfigParser
import unittest
import os
import logging

__author__ = 'Keith Robertson <kroberts@redhat.com>'

class solutionTest(unittest.TestCase):

    def setUp(self):
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
        self.api.disconnect();


    def testGetSolution(self):
        print "---testGetSolution---"
        sid = self.config.get('testGetSolution', 'solutionID')
        print "Getting solution %s" % sid
        try:
            sol = self.api.solutions.get(sid)
            print sol
            assert sol is not None
            print "Solution title(%s)" % sol.get_title()
            assert sol.get_title() == self.config.get('testGetSolution', 'title')
            print "Solution authorSSOName(%s)" % sol.get_authorSSOName()
            assert sol.get_authorSSOName() == self.config.get('testGetSolution', 'authorSSOName')
        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")
        pass

    def testFilterSolutions(self):
        print "---testFilterSolutions---"
        try:
            solAry = self.api.solutions.list(self.config.get('testFilterSolutions', 'keyword'),
                                             title=self.config.get('testFilterSolutions', 'title'))
            assert solAry is not None
            for sol in solAry:
                print "Found the following solution:"
                sol.toXml()
        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")
        pass

    def testAddUpdateSolution(self):
        print "---testAddUpdateSolution---"

        sol = solution.fromProps(createdBy='rhn-support-cbredese',
                                 title=self.config.get('testAddUpdateSolution', 'title'),
                                 summary="testAddUpdateSolution",
                                 kcsState='wip',
                                 resolution='test')
        print "---Adding solution---"
        sol.toXml()
        try:
            doc = self.api.solutions.add(sol)
            assert doc.get_id() is not None
            print "---Updating solution---"
            doc.toXml()
            sol.set_resolution(self.config.get('testAddUpdateSolution', 'newtext'))
            sol.toXml()
            assert sol.get_resolution().get_text() == self.config.get('testAddUpdateSolution', 'newtext')
            sol.update()
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
    cases = unittest.defaultTestLoader.getTestCaseNames(solutionTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(solutionTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
