import json

path = '/config/config.json'

with open(path) as f:
  config = json.load(f)