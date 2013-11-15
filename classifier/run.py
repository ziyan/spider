#!/usr/bin/env python

import os
import sys

lib_path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))
if lib_path not in sys.path:
    sys.path[0:0] = [lib_path]

import utils
import clusterers
import processors
import simplejson as json
import os
import argparse
import analyzers
import tokenizers
import numpy as np
from sklearn import svm

def main(args):

    path = utils.get_data_path(args.site[0])
    urls = utils.load_urls(path)

    # load data
    data = [utils.load_data(path, id) for id, url in enumerate(urls)]

    # process data
    processor = processors.Processor(data, tokenizer=tokenizers.GenericTokenizer, analyzer=analyzers.LongestAnalyzer)
    features = processor.extract()

    # clustering
    clusterer = clusterers.DBSCAN()
    labels = clusterer.cluster(features).labels_

    # score
    pages, features, labels = processor.prepare(labels)

    # train
    clf = svm.SVC()
    n = int(len(labels) * 0.8)
    print np.sum(labels[:n])
    print clf.fit(features[:n], labels[:n])

    print np.sum(clf.predict(features[n:]) == labels[n:])
    print len(labels[n:])
    
    with open(os.path.join(path, 'svm.json'), 'w') as f:
        f.write(json.dumps(pages, indent=2, ensure_ascii=False).encode('utf8'))

def parse_args():
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description='Run the whole pipeline on site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
