from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup

import sys

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

## Small hack for working with bdist_wininst.
## See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
#if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
#    for file_info in data_files:
#        file_info[0] = '/PURELIB/%s' % file_info[0]


setup(name='Gchecky',
      version='0.1',
      url='http://code.google.com/p/gchecky/',
      author='Evgeniy Tarassov',
      author_email='etarassov@gmail.com',
      description='Python wrapper for Google Checkout API',
      license='Apache License 2.0',
      packages=['gchecky',],
      package_data={'gchecky':['docs/*.txt','docs/*.html']},
      data_files=[],
      scripts=[],
)

