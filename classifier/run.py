import os
import argparse
import preprocessors
import clusterers
import simplejson as json
import numpy as np
import collections

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

def main(args):

    path = get_data_path(args.site[0])
    urls = load_urls(path)

    # load data
    data = []
    for id, url in enumerate(urls):
        data.append(load_data(path, id))

    # process data
    preprocessor = preprocessors.Preprocessor(data)
    datapoints, features = preprocessor.extract()

    # cluster
    clusterer = clusterers.DBSCAN()
    db = clusterer.cluster(features)

    # debug
    clusters = collections.defaultdict(list)
    for id, label in enumerate(db.labels_):
        clusters[int(label)].append(datapoints[id]['html'])

    print json.dumps(clusters, indent=2)

def parse_args():
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description='Run classifier on site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
