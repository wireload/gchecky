#!/bin/bash

# regenerate docs
rm -rf docs/*
epydoc --html -o docs gchecky

# purge MANIFEST file and python byte-code files
rm MANIFEST \
   samples/*.pyc \
   samples/django/*.pyc \
   samples/django/gcheckout*.pyc \
   samples/gbutton/*.pyc

# build everything
python setup.py build

# create source distribution
python setup.py sdist

# and binary distributions
python setup.py bdist bdist_wininst

# TODO: provide 'docs/man/*' for the target 'bdist_rpm'

# clean up
python setup.py clean
