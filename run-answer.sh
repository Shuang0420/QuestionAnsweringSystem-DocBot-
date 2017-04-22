#!/bin/bash

source ./env_setup.sh
# Answerer should always take two arguments: input file (.txt, though .html will be present) and file of questions (.txt).
# ./answer "$1" "$2"
python answer.py "$1" "$2"
