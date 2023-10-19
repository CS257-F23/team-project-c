#!/bin/bash
python3 -m coverage run --source ProductionCode,app,pyspill -m unittest discover Tests &&
python3 -m coverage html &&
open htmlcov/index.html
