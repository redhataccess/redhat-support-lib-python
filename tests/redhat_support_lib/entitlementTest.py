'''
Created on Sep 28, 2012

@author: Rex White
'''
from optparse import OptionParser
from redhat_support_lib.api import API
import ConfigParser
import unittest
import os
import logging

__author__ = 'Rex White <rexwhite@redhat.com>'

class entitlementTest(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('strata.cfg')
        self.user = self.config.get('strata', 'external_username')
        if (self.user.startswith('$')):
            self.user = os.environ.get(self.user[1:])
            print "Username: ", self.user
            logging.log(logging.DEBUG, "Username: %s" % self.user)

        self.passwd = self.config.get('strata', 'external_password')
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


    # This is just a place-holder and needs to be replaced with a more meaningful test, just as soon as
    # someone can explain entitlements to me in sufficient detail
    def testGetEntitlements(self):
        print "---testGetEntitlements---"
        entAry = self.api.entitlements.list(activeOnly=True, product="JBoss Communications Platform")

        self.assertNotEqual(entAry, None)

        print "entitlements:"
        print "found", len(entAry), "entitlements."


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
    cases = unittest.defaultTestLoader.getTestCaseNames(entitlementTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(entitlementTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
