'''
Created on Dec 11, 2012

@author: Huan Zhang
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
import ConfigParser
import unittest
import os
import logging

__author__ = 'Huan Zhang <hzhang@redhat.com>'

class symptomTest(unittest.TestCase):


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
        self.api.disconnect();


    def testAddSymptom(self):
        print "---testAddSymptom---"
        try:
            print "make a case so we can add a symptom to it..."

            # get product list for this user
            print "===================================================="
            print "Getting list of products for this user:"
            productAry = self.api.products.list()
            self.assertNotEqual(productAry, None)
            product = productAry[0]

            # get version list for a product
            print "===================================================="
            print "Getting versions for one of the products:"
            versionAry = product.get_versions()
            self.assertNotEqual(versionAry, None)
            version = versionAry[0]

            # create new case object
            case = self.api.im.makeCase()

            # set required initial fields
            case.product = product.name
            case.version = version
            case.summary = 'This is only a test.'
            case.description = 'This is an automatically generated test case.  Feel free to delete it.'
            case.severity = '3 (Normal)'

            # support level and case group are a little hard to set directly, so skip them

            print "===================================================="
            print "Creating a case that looks like this:"
            print case.toXml()
            print "----------------------------------------------------"
            doc = self.api.cases.add(case)

            print "===================================================="
            print "Getting our newly created case:"
            newdoc = self.api.cases.get(doc.caseNumber)
            print "----------------------------------------------------"
            print "Which looks like this:"
            print newdoc.toXml()

            print "===================================================="
            print "Adding a symptom to our newly created case:"
            # create new symptom object
            sym = self.api.im.makeSymptom(caseNumber=doc.caseNumber,
                                          summary='SUMMARY', category='CPP',
                                          uri='URI', description='DES',
                                          data='TRACE', location='LOC')

            print sym.toXml()

            print "----------------------------------------------------------------------"
            sym = self.api.symptoms.add(sym)
            print sym.location
            self.assertNotEqual(sym.location, None,)

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")

    def testExtractSymptomFromString(self):
        print "---testExtractSymptomFromString---"
        try:
            print "----------------------------------------------------------------------"
            f = open('server.log', 'r')
            # sym = self.api.symptoms.extractFromFile('/home/kroberts/Programs/jbdevstudio/runtimes/jboss-eap/standalone/log/server.log')
            serverlog = f.read()
            sym = self.api.symptoms.extractFromStr(serverlog)
            print "Number of returned symptoms: ", len(sym)
            self.assertNotEqual(sym[0].get_type(), None)

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")

    def testExtractSymptomFromFile(self):
        print "---testExtractSymptomFromFile---"
        try:
            print "----------------------------------------------------------------------"
            sym = self.api.symptoms.extractFromFile('server.log')
            print "Number of returned symptoms: ", len(sym)
            self.assertNotEqual(sym[0].get_type(), None)

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")



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
    cases = unittest.defaultTestLoader.getTestCaseNames(symptomTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(symptomTest, args))
    unittest.TextTestRunner().run(testSuite)
else:
    class options:
        debug = True
