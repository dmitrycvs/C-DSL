#!/bin/bash

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running ANTLR..."
java -jar antlr/antlr-4.13.2-complete.jar -visitor DrawShapes.g4 -Dlanguage=Python3

echo "Done!"
