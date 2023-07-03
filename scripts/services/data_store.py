import json
import os

def save(tilemap, path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError

        with open(os.path.join(path, 'tilemap.json'), 'w') as t:
            json.dump(tilemap, t, indent=2, sort_keys=True)

    except (FileNotFoundError) as e: 
        print(e)

def load(path):
    tilemap = {}

    try:
        with open(os.path.join(path, 'tilemap.json')) as t:
            tilemap = json.load(t)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(e)
    
    return tilemap
