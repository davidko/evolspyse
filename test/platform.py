import unittest

from spyse.core.platform.platform import Platform
from spyse.core.platform.constants import Dist, NsMode, ThreadMeth

class PlatformTestCase(unittest.TestCase):
    """Test the platform"""
    def test_up_down(self):
        port = 9000
        dist = Dist.NONE
        threadmeth = ThreadMeth.NORMAL
        poolsize = 100
        env = 'normal'
        nsmode = NsMode.NONE
        print 'The tester will now start up the platform.'
        p = Platform(port=port, threadmeth=threadmeth, poolsize=poolsize, dist=dist, env=env, nsmode=nsmode)
        assert p.is_running()
        assert p.running
        assert p.population > 0
        print "The tester will now shut down the platform."
        p.shutdown()
        assert not p.is_running()
 
if __name__ == "__main__":
    unittest.main()
