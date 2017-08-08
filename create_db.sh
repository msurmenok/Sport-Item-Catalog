#!/usr/bin/env bash
psql -c "CREATE DATABASE catalog;"
python database_setup.py
python load_data.py