"""Spyse core package"""
__version__ = '0.2'

#
# Import the names of all core packages into the "core" package namespace.
#
# The symbol table of each core package contains the names of basic
# objects in that package.  Hence, importing those packages here makes
# the names of those basic objects available to the importer of this package,
# spyse.core, via 'spyse.core.pkg.foo'.
#

package_names = [ 'platform', 'agents', 'behaviours', 'protocols', 'content', 'mts', 'semant' ]
for n in package_names:
    exec 'import ' + n

