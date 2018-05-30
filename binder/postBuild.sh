#!/usr/bin/env bash

cd ..
python setup.py install
jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.35 --no-build &&
jupyter labextension install bqplot@0.3.6 --no-build &&
jupyter lab clean && jupyter lab build

