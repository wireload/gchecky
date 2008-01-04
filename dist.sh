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

# create source distribution
python setup.py sdist

# and binary distribution
python setup.py bdist
