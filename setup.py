#!/usr/bin/env python

# Based on http://wiki.python.org/moin/DistutilsAutoPackageDiscovery

import os

def isPackage( filename ):
    return (
        os.path.isdir(filename) and
        os.path.isfile( os.path.join(filename,'__init__.py'))
    )

def packagesFor( filename, basePackage="" ):
    """Find all packages in filename"""
    set = {}
    for item in os.listdir(filename):
        dir = os.path.join(filename, item)
        if isPackage( dir ):
            if basePackage:
                moduleName = basePackage+'.'+item
            else:
                moduleName = item
            set[ moduleName] = dir
            set.update( packagesFor( dir, moduleName))
    return set

packages = packagesFor( ".", basePackage="spyse" )

from distutils.core import setup

setup(name="Spyse",
      description="Smart Python Simulation Environment",
      version="0.2",
      author="Andre Meyer",
      author_email="Andre.Meyer@spammerbgone.tno.nl",
      url="http://python.openspace.nl/spyse/SpyseHome",
      license="LGPL",
      package_dir=packages,
      packages=packages.keys()
)
