#!/bin/bash
# Cron job script to run chromadb_monitor.py once per day
cd "$(dirname "$0")"
python chromadb_monitor.py
