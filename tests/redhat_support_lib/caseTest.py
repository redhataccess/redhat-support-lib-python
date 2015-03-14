'''
Created on Apr 10, 2012

@author: Keith Robertson
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.brokers import cases, case
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
import ConfigParser
import unittest
import os
import logging

__author__ = 'Keith Robertson <kroberts@redhat.com>'

class caseTest(unittest.TestCase):

    def setUp(self):
        print ""
        print "*********************************************************************"
        print "*********************************************************************"
        print "*********************************************************************"
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


    def testAddGetCase(self):
        print "---testAddGetCase---"

        try:
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

            # Verify fields in new case are sane
            print "===================================================="
            print "Verifying a bunch of stuff..."
            self.assertEqual(newdoc.caseNumber, doc.caseNumber)
            self.assertEqual(newdoc.product, product.name)
            self.assertEqual(newdoc.version, version)
            self.assertEqual(newdoc.summary, 'This is only a test.')
            self.assertEqual(newdoc.description, 'This is an automatically generated test case.  Feel free to delete it.')
            self.assertEqual(newdoc.severity, '3 (Normal)')

            self.assertEqual(newdoc.closed, False)
            self.assertEqual(newdoc.escalated, False)
            self.assertEqual(newdoc.uri, self.url + '/rs/cases/' + doc.caseNumber)
            self.assertEqual(newdoc.status, 'Waiting on Red Hat')

            # try to clean up after ourselves
            print "Everything looks fine, so close the case we created:"
            newdoc.status = 'Closed'
            newdoc.update();

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")

    def testUpdateCase(self):
        print "---testUpdateCase---"
        try:
            # get product list for this user
            print "===================================================="
            print "Getting list of products for this user:"
            productAry = self.api.products.list()
            self.assertNotEqual(productAry, None)
            product1 = productAry[0]
            product2 = productAry[1]

            # get version list for a product
            print "===================================================="
            print "Get a list of versions for product: ", product1.name
            version1Ary = product1.get_versions()
            self.assertNotEqual(version1Ary, None)
            version1 = version1Ary[0]
            print "===================================================="
            print "Get a list of versions for product: ", product2.name
            version2Ary = product2.get_versions()
            self.assertNotEqual(version2Ary, None)
            version2 = version2Ary[0]

            # create a new case using the API instance maker method
            case = self.api.im.makeCase(summary='Test Case',
                                        product=product1.name,
                                        version=version1,
                                        description='This is only a test!',
                                        status='Waiting on Red Hat',
                                        type_='Bug',
                                        suppliedName='Supplied Name',
                                        suppliedPhone='212 123-4567',
                                        suppliedEmail='email@company.com',
                                        severity='3 (Normal)')

            print "===================================================="
            print "Create a new case that looks like this:"
            print case.toXml()

            # add new case to strata
            print "----------------------------------------------------"
            self.api.cases.add(case)

            # get newly created case
            print "===================================================="
            print "Get the case we just created..."
            case = self.api.cases.get(case.get_caseNumber())

            print "----------------------------------------------------"
            print "Our new case:"
            print case.toXml()

            # fields I can change
            print "===================================================="
            print "Change some fields in the case..."
            case.type_ = 'Info'
            case.severity = '4 (Low)'
            case.status = 'Waiting on Customer'
            case.alternateId = 'new alternate ID'
            case.product = product2.name
            case.version = version2
            # case.folder i.e. case group is user dependent so let's skip it for now

            print "Our case now looks like this:"
            print case.toXml()
            print "===================================================="
            print "Update the case via strata..."
            print case.update()

            print "===================================================="
            print "Retrieve the updated case..."
            case = self.api.cases.get(case.caseNumber)
            print "----------------------------------------------------"
            print "Updated case looks like this:"
            print case.toXml()

            # validate fields in new case
            print "===================================================="
            print "Validate a bunch of stuff..."
            self.assertEqual(case.type_, 'Info')
            self.assertEqual(case.severity, '4 (Low)')
            self.assertEqual(case.status, 'Waiting on Customer')
            self.assertEqual(case.alternateId, 'new alternate ID')  # can't set during create!
            self.assertEqual(case.product, product2.name)
            self.assertEqual(case.version, version2)

            # these fields should have something in them, but their contents is difficult to predict,
            # so just make sure they're not empty
            self.assertNotEqual(case.id, None)
            self.assertNotEqual(case.createdBy, None)
            self.assertNotEqual(case.createdDate, None)
            self.assertNotEqual(case.lastModifiedBy, None)
            self.assertNotEqual(case.lastModifiedDate, None)
            self.assertNotEqual(case.accountNumber, None)
            self.assertNotEqual(case.contactName, None)
            self.assertNotEqual(case.contactSsoUsername, None)

            # the following fields should be empty
            self.assertEqual(case.component, None)
            self.assertEqual(case.reference, None)
            self.assertEqual(case.notes, None)
            self.assertEqual(case.escalated, False)

            # clean up after ourselves
            print "Everything looks good, so close the case we opened..."
            case.status = 'Closed'
            case.update();

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")

        pass

    def testListCases(self):
        print "---testListCases---"
        try:
            # create a new case so we know our search will return at least ONE case...\

            # get product list for this user
            print "===================================================="
            print "Getting list of products for this user:"
            productAry = self.api.products.list()
            print "===================================================="

            self.assertNotEqual(productAry, None)
            product = productAry[0]

            # get version list for a product
            print "Getting list of versions for product: ", product.name
            versionAry = product.get_versions()
            print "===================================================="
            self.assertNotEqual(versionAry, None)
            version = versionAry[0]

            # create a new case using the API instance maker method
            print "Creating a new case..."
            case = self.api.im.makeCase(summary='Test Case',
                                        product=product.name,
                                        version=version,
                                        description='This is only a test! (testListCases)',
                                        status='Waiting on Red Hat',
                                        type_='Bug',
                                        suppliedName='Supplied Name',
                                        suppliedPhone='212 123-4567',
                                        suppliedEmail='email@company.com',
                                        severity='3 (Normal)')

            print "Which look like this:"
            print case.toXml()

            # add new case to strata
            print "===================================================="
            print "Adding our new case..."
            self.api.cases.add(case)

            # get newly created case
            print "===================================================="
            print "Getting the new case we just added..."
            case = self.api.cases.get(case.get_caseNumber())

            # search for cases
            print "===================================================="
            print "Searching for cases..."
            caseAry = self.api.cases.list(includeClosed=False)
            self.assertNotEqual(caseAry, None)

            print "----------------------------"
            print "Cases Found: ", len(caseAry)
            print "----------------------------"

            # make sure there are no duplicates, if feasible
            if len(caseAry) < 5000:
                print "===================================================="
                print "Checking for duplicate cases..."
                caseSet = set()
                for case in caseAry:
                    caseSet.add(case.caseNumber)

                if len(caseAry) != len(caseSet):
                    print "There was a duplicate case returned!"
                    self.fail()

                print "No duplicates found."

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
    cases = unittest.defaultTestLoader.getTestCaseNames(caseTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(caseTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
