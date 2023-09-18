from bottle import run, get
import os.path
from const import store_directory
import json

@get('/api/forecast')
def forecast():
    file_path = f'{store_directory}forecast.json'
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return json.load(f)
    else:
            return {}

@get('/api/status')
def status():
    file_path = f'{store_directory}status.json'
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return json.load(f)
    else:
            return {}

run(host = '0.0.0.0', port = 8000, quiet=True)
