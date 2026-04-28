#!/usr/bin/env python
"""
Script to export data from SQLite database to JSON fixtures.
Run this before deploying to export your current data.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roster_system.settings')
django.setup()

from django.core.management import call_command
from django.core.management import execute_from_command_line

# Export all data to fixtures
print("Exporting data from SQLite database...")

# Export data for each app
apps = ['auth', 'core']

for app in apps:
    fixture_file = f'{app}_data.json'
    print(f"Exporting {app} data to {fixture_file}...")
    with open(fixture_file, 'w') as f:
        call_command('dumpdata', app, stdout=f, indent=2)

print("Data export complete!")
print("Copy these JSON files to your deployed app and run:")
print("python manage.py loaddata auth_data.json core_data.json")