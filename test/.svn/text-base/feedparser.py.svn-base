import unittest
from pprint import pprint

# copied from http://www-106.ibm.com/developerworks/library/os-ecant/index.html?ca=drs-tp2604

import spyse

class SpyseTest(unittest.TestCase):
    """A test class for the feedparser module"""
    
    def setUp(self):
        """
        set up data used in the tests.
        setUp is called before each test function execution.
        """
        self.developerWorksUrl = "testData/developerworks.rss"       

    def testParse09Rss(self):
        """
        Test a successful run of the parse function for a
        0.91 RSS feed.
        """
        print "FeedparserTest.testParse09RSS()"
        
        result = feedparser.parse(self.developerWorksUrl)
        pprint(result)

        self.assertEqual(0, result['bozo'])
        
        self.assert_(result is not None)
        channel = result['channel']
        self.assert_(channel is not None)
        chanDesc = channel['description']
        self.assertEqual(u'The latest content from IBM developerWorks',
            chanDesc)
        
        items = result['items']
        self.assert_(items is not None)
        self.assert_(len(items)> 3)
        firstItem = items[0]
        title = firstItem['title']
        self.assertEqual(u'Build installation packages with solution installation and deployment technologies', title)

    def tearDown(self):
        """
        tear down any data used in tests
        tearDown is called after each test function execution.
        """
        pass
                
if __name__ == '__main__':
    unittest.main()

