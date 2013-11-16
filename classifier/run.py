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
from sklearn.metrics import precision_recall_curve, auc, classification_report

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
    clf = svm.SVC(verbose=True, kernel='linear', probability=True, random_state=0)
    n = int(len(labels) * 0.5)
    print np.sum(labels[:n])

    proba = clf.fit(features[:n], labels[:n]).predict_proba(features[n:])
    precision, recall, thresholds = precision_recall_curve(labels[n:], proba[:, 1])

    print 'precision:'
    print precision
    print 'recall:'
    print recall
    print 'thresholds:'
    print thresholds
    
    area = auc(recall, precision)
    print 'area under curve: %f' % area

    print '======'
    predicted = clf.predict(features[n:])
    print classification_report(labels[n:], predicted)
    
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
