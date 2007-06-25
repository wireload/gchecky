#!/bin/bash
epydoc --html -o docs gchecky
python setup.py sdist
python setup.py bdist
