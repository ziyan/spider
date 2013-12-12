import os
import simplejson as json
import itertools

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

def load_gold_text(path, id):
    with open(os.path.join(path, '%03d.txt' % id)) as f:
        data = f.read()
    return data

def consolidate_selectors(selectors):

    for selector1, selector2 in itertools.product(selectors, repeat=2):
        if selector1 is selector2:
            continue

        # element tag name needs to match
        names1 = ' > '.join([s['name'] for s in selector1])
        names2 = ' > '.join([s['name'] for s in selector2])
        if names1 != names2:
            continue

        for part1, part2 in zip(selector1, selector2):
            if part1['id'] != part2['id']:
                part1['id'] = ''
                part2['id'] = ''
            classes = list(set(part1['classes']) & set(part2['classes']))
            part1['classes'] = classes
            part2['classes'] = classes

    consolidated = dict()
    for selector in selectors:
        paths = []
        for part in selector:
            path = part['name']
            if part['id']:
                path += '#' + part['id']
            if part['classes']:
                path += '.' + '.'.join(part['classes'])
            paths.append(path)
        consolidated[' > '.join(paths)] = selector

    return consolidated
