import os
import simplejson as json

def get_data_path(site):
    return os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', site))

def load_urls(path):
    with open(os.path.join(path, 'urls')) as f:
        urls = f.readlines()
    return urls

def load_data(path, id):
    with open(os.path.join(path, '%03d.json' % id)) as f:
        data = json.load(f)
    return data

