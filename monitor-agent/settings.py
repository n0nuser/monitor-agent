import os
import json
from types import SimpleNamespace

dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "settings.json"
abs_file_path = os.path.join(dir, rel_path)
f = open(abs_file_path, "r")
data = f.read()
# Parse JSON into an object with attributes corresponding to dict keys.
# https://stackoverflow.com/a/15882054
settings = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
