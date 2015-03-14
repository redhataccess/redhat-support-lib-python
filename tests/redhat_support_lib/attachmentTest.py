'''
Created on Apr 10, 2012

@author: Keith Robertson
'''
from optparse import OptionParser
from redhat_support_lib.api import API
from redhat_support_lib.infrastructure.errors import RequestError, ConnectionError
import ConfigParser
import os
import unittest
import logging

__author__ = 'Keith Robertson <kroberts@redhat.com>'


class attachmentTest(unittest.TestCase):

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
        self.api.disconnect()

    def testFilterAttachments(self):
        print "---testFilterAttachments---"

        try:
            # create a new case and add an attachment upon which to filtereth

            print "make a case so we can add an attachment to it..."

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
            print "Attach a file to our pretty new case..."

            aFile = "attachmentTest.py"
            public = True
            description = "A description of the file."

            resp = self.api.attachments.add(caseNumber=caseNumber,
                                            public=public,
                                            fileName=aFile,
                                            description=description)

            uuid = resp.uuid

            print "===================================================="
            print "Search for our attachment..."

            aAry = self.api.attachments.list(caseNumber=doc.caseNumber,
                                             uuid=uuid)
            assert aAry is not None

            print "----------------------------------------------------"
            for a in aAry:
                print "Found the following attachment:"
                print a.toXml()
                self.assertEqual(a.description, description)
                self.assertEqual(a.uuid, uuid)

            # try to clean up after ourselves
            print "===================================================="
            print "Everything looks ok so clean up after ourselves..."
            newdoc.status = 'Closed'
            newdoc.update()

        except RequestError, re:
            self.fail("Unable to connect to support services API.  Reason: %s %s" % (re.status, re.reason))
        except ConnectionError:
            self.fail("Problem connecting to the support services API.  Is the service accessible from this host?")

    def testAddGetAttachment(self):
        print "---testAddAttachment---"

        try:
            print "make a case so we can add an attachment to it..."

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
            print "Attach a file to our pretty new case..."

            aFile = "attachmentTest.py"
            public = True
            description = "A description of the file."

            self.api.attachments.add(
                caseNumber=newdoc.caseNumber,
                public=public,
                fileName=aFile,
                description=description)

            print "===================================================="
            print "Get attachment list from case:"
            attachmentAry = newdoc.get_attachments()

            # look for our attachment
            print ""
            print "----------------------------------------------------"
            print "Look for our attachment..."
            found = False
            for att in attachmentAry:
                if att.fileName == aFile:
                    uuid = att.uuid
                    found = True

            self.assertEqual(found, True)

            # try to GET the attachment from our case
            print "Downloading attachment..."
            self.api.attachments.get(caseNumber=newdoc.caseNumber, attachmentUUID=uuid, fileName="downloaded_attachment")

            # we should probably validate the contents of the downloaded file

            # try to clean up after ourselves
            print "Everything looks ok so clean up after ourselves..."
            newdoc.status = 'Closed'
            newdoc.update()

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
    if options.quiet is False:
        logging.basicConfig(level=logging.DEBUG)

    # get testcase list
    cases = unittest.defaultTestLoader.getTestCaseNames(attachmentTest)

    # handle 'list' option
    if options.list:
        for case in cases:
            print case
        quit()

    # run all tests if none specified
    if args is None or len(args) == 0:
        args = cases

    testSuite = unittest.TestSuite(map(attachmentTest, args))
    unittest.TextTestRunner().run(testSuite)

else:
    # set debug option to True when running as a module
    class options:
        debug = True
