from bottle import run, get
import os.path
from const import store_directory
import json
from typing import Any
from logger import logger

@get('/api/forecast')
def forecast():
    return load_file(f'{store_directory}forecast.json')

@get('/api/status')
def status():
    return load_file(f'{store_directory}status.json')

@get('/api/raw')
def raw():
    return load_file(f'{store_directory}gfsdata.json')
    
def load_file(file_path: str) -> Any:
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return json.load(f)
    else:
            return {}

run(host = '0.0.0.0', port = 8000, quiet=True)
