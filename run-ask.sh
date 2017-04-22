#!/bin/bash

source ./env_setup.sh
# Asker should always take two arguments: input file (.txt, though .html will be present) and number of questions to ask.
python ask.py "$1" "$2"