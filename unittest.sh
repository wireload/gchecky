#!/bin/bash
export EXEC_DIR=`dirname $0`
export PYTHONPATH=$EXEC_DIR
cd $EXEC_DIR
python all_tests.py
