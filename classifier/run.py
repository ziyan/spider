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
from sklearn import svm, preprocessing, cross_validation
from sklearn.metrics import precision_recall_curve, auc, classification_report
import collections

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

    # prepare features
    clusters, features, labels = processor.prepare(labels)

    # scale features
    features = preprocessing.scale(features)


    rs = cross_validation.KFold(len(labels), n_folds=4, shuffle=True, random_state=0)
    for train_index, test_index in rs:
        print 'training size = %d, testing size = %d' % (len(train_index), len(test_index))

        clf = svm.SVC(verbose=True, kernel='linear', probability=False, random_state=0, cache_size=2000, class_weight='auto')
        clf.fit(features[train_index], labels[train_index])

        predicted = clf.predict(features[test_index])
        print classification_report(labels[test_index], predicted)

    ham = collections.defaultdict(dict)
    spam = collections.defaultdict(dict)

    for id, cluster in clusters.iteritems():
        for page in cluster['pages'].values():
            content = ''
            for text in page['texts']:
                content += ' '.join(text['text'])
            if cluster['label'] is 1:
                ham[url][id] = content
            else:
                spam[url][id] = content


    with open(os.path.join(path, 'svm.json'), 'w') as f:
        f.write(json.dumps({'ham': ham, 'spam': spam}, indent=2, ensure_ascii=False).encode('utf8'))

def parse_args():
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description='Run the whole pipeline on site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
