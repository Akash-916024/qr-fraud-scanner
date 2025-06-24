#!/usr/bin/env bash

# Install ZBar library for pyzbar
apt-get update && apt-get install -y libzbar0

# Install Python dependencies
pip install -r requirements.txt
