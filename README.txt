Installation
============
Installation should be as easy as typing:
  $ python setup.py install

If you get an error similar to:
  The required version of setuptools (>=0.6c7) is not available, and
  can't be installed while this script is running. Please install
   a more recent version first.

Then try running:
  $ sudo python ez_setup.py

This should install/update setuptools on your system. If you don't have root
privileges then you should try to install and use setuptools locally.
Something like:
  $ export PYTHONPATH
  $ python ez_setup.py setuptools --install-dir=<the_location>

Be sure to permanently add <the_location> to your python path (for example
via PYTHONPATH environment variable).

#TODO:

Documentation
=============
To generate documentation use epydoc packages:
  $ cd /path/to/gchecky
  $ epydoc --html -o docs gchecky

Read epydoc manual for other output formats and options:
  $ epydoc -h

To install epydoc package on:
  $ sudo easy_install epydoc
or to some local directory:
  $ easy_install --install-dir=<the_location> epydoc
or download the installation package from http://epydoc.sourceforge.net/
and follow the instructions.
