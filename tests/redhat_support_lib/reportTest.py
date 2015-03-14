from optparse import OptionParser
from redhat_support_lib.api import API
import ConfigParser
import unittest
import os
import shutil

__author__ = 'Keith Robertson <kroberts@redhat.com>'
__author__ = 'tdwalsh'



class reportTest(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('strata.cfg')
        self.user = self.config.get('strata', 'username')
        if (self.user.startswith('$')):
            self.user = os.environ.get(self.user[1:])
            print "Username: ", self.user
            logging.log(logging.DEBUG, "Username: %s" % self.user)

        self.passwd = self.config.get('strata', 'password')
        if (self.passwd.startswith('$')):
            self.passwd = os.environ.get(self.passwd[1:])
            logging.log(5, "password: %s" % self.passwd)

        self.url = self.config.get('strata', 'url')
        if (self.url.startswith('$')):
            self.url = os.environ.get(self.url[1:])
            print "url: ", self.url

        pass

    def tearDown(self):
        pass

    def testMakeReort(self):
        print "---testMakeReport---"
        fileName = API.make_report(self.config.get('testMakeReport', 'path'),
                                   {'key':'value', 'key2':'value2'})

        if fileName:
            print 'Report file is {0}'.format(fileName)
            rpt = API.process_report_file(fileName)
            binding_ary = rpt.get_binding()
            for b in binding_ary:
                print 'Found a binding with name: {0}'.format(b.get_name())
            print 'Removing directory {0}'.format(os.path.dirname(fileName))
            # Dangerous to leave by default so I'm commenting it out.
            # shutil.rmtree(os.path.dirname(fileName))
            pass

        else:
            self.fail("Problem generating report file")



# can be run as python -m unittest rhhelp.report.reportTest
# export PYTHONPATH=/home/twalsh/share/rh-help/src
if __name__ == '__main__':
    unittest.main()

