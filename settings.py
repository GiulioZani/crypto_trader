import json
from bunch import Bunch

with open('settings.json') as f:
    settings = Bunch(json.load(f))

