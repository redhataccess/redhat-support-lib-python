'''
Created on Aug 17, 2012

@author: Rex White
'''
import unittest
import logging

__author__ = 'Rex White <rexwhite@redhat.com>'

if __name__ == "__main__":

    # enable verbose logging
    logging.basicConfig(level=logging.DEBUG)

    # list of modules to search for test cases
    testList = ['caseTest', 'commentTest', 'attachmentTest', 'articleTest', 'solutionTest', 'diagnoseTest', 'entitlementTest', 'productTest', 'symptomTest']

    suite = unittest.defaultTestLoader.loadTestsFromNames(testList)
    unittest.TextTestRunner().run(suite)
