#!/bin/bash

virtualenv .venv
source ./.venv/bin/activate
pip install -e git+https://github.com/stackforge/python-cueclient.git#egg=python-cueclient