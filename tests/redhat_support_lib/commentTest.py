'''
Created on Apr 10, 2012

@author: Keith Robertson
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
import ConfigParser
import unittest
import os
import logging

__author__ = 'Keith Robertson <kroberts@redhat.com>'

class commentTest(unittest.TestCase):

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


    def testGetOtherComment(self):
        print "--- testGetOtherComment ---"
        print "Checking to see if we can retrieve comments from cases that are not visible to us..."
        try:
            # create a sparse case so we'll have a case number that is guaranteed to be valid for this user
            print "Creating a sparse case..."
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
            caseNumber = doc.caseNumber

            cmnt = self.api.comments.get(caseNumber=caseNumber,
                                         commentID="a0aA0000007vrRfIAI")  # this is a real comment from a live case
            print "Retrieved comment:"
            print cmnt.toXml()

            if cmnt == None or cmnt.id == None:
                success = True
            else:
                success = False

            # try to clean up after ourselves
            print "===================================================="
            print "Clean up after ourselves..."
            doc.status = 'Closed'
            doc.update();

            if success == False:
                self.fail("Should not have been able to retrieve comment!")

        except RequestError, re:
            print "Attempt was not successful (as it should not be.)"
            print "Clean up after ourselves..."
            doc.status = 'Closed'
            doc.update();

        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")


    def testFilterComments(self):
        print "---testFilterComments---"

        try:
            # create a new case and add a comment for use in testing the list function

            print "make a case so we can add a comment to it..."

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
            caseNumber = doc.caseNumber

            print "===================================================="
            print "Getting our newly created case:"
            newdoc = self.api.cases.get(caseNumber)
            print "----------------------------------------------------"
            print "Which looks like this:"
            print newdoc.toXml()

            print "===================================================="
            print "Add a comment to our new case..."

            text = "PyUnit test text"
            public = True

            com = self.api.im.makeComment(caseNumber=caseNumber,
                                          text=text,
                                          public=public)

            print "The comment looks like this:"
            print com.toXml()

            print "----------------------------------------------------"
            print "Adding comment..."
            doc = self.api.comments.add(com)
            print "----------------------------------------------------"
            print "Returned results: "
            print doc.toXml()
            self.assertNotEqual(doc.id, None)
            self.assertNotEqual(doc.caseNumber, None)

            print "===================================================="
            print "Try to find our new comment..."

            comAry = self.api.comments.list(caseNumber=caseNumber,
                                            id=doc.id)
            self.assertNotEqual(comAry, None)

            print "----------------------------------------------------"
            for com in comAry:
                print "Found the following comment:"
                print com.toXml()

            # try to clean up after ourselves
            print "===================================================="
            print "Everything looks ok so clean up after ourselves..."
            newdoc.status = 'Closed'
            newdoc.update();

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason:  %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")


    def testAddGetComment(self):
        print "---testAddComment---"
        try:
            # create a new case and add a comment for use in testing the list function

            print "make a case so we can add a comment to it..."

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
            caseNumber = doc.caseNumber

            print "===================================================="
            print "Getting our newly created case:"
            newdoc = self.api.cases.get(caseNumber)
            print "----------------------------------------------------"
            print "Which looks like this:"
            print newdoc.toXml()

            print "===================================================="
            print "Add a comment to our new case..."

            text = "PyUnit test text"
            public = True

            com = self.api.im.makeComment(caseNumber=caseNumber,
                                          text=text,
                                          public=public)

            print "The comment looks like this:"
            print com.toXml()

            print "----------------------------------------------------"
            print "Adding comment..."
            doc = self.api.comments.add(com)
            print "----------------------------------------------------"
            print "Returned results: "
            print doc.toXml()
            self.assertNotEqual(doc.id, None)
            self.assertNotEqual(doc.caseNumber, None)

            # verify the new comment
            print "===================================================="
            print "Verify comment:"
            print "Retrieving case..."
            case = self.api.cases.get(caseNumber)
            print "----------------------------------------------------"
            print "Retrieved case:\n"
            print case.toXml()

            commentAry = case.get_comments()
            self.assertNotEqual(commentAry, None)

            print "Checking case for our comment..."
            found = False
            for aComment in commentAry:
                if aComment.get_text() == text:
                    print "--> found comment"
                    if aComment.get_public() == True:
                        print "--> visibility is correct"
                        found = True
                    else:
                        print "--> visibility is WRONG!!"
                        print "visibility = ", aComment.get_public()

            # try to clean up after ourselves
            print "===================================================="
            print "Clean up after ourselves..."
            newdoc.status = 'Closed'
            newdoc.update();

            # fail the test if we didn't find our comment
            if found == False:
                print "===================================================="
                self.fail("--> Did not find comment")

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
    cases = unittest.defaultTestLoader.getTestCaseNames(commentTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(commentTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
