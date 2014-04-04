#!/usr/bin/env python

import os
import sys

lib_path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))
if lib_path not in sys.path:
    sys.path[0:0] = [lib_path]

import utils
import os
import argparse
import processors
import tokenizers
import analyzers
import clusterers
import collections
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm, preprocessing, cross_validation
from sklearn.metrics import precision_recall_curve, auc, classification_report, precision_recall_fscore_support
import random

def main(args):

    extractor = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'label.py')
    path = utils.get_data_path(args.site[0])
    urls = utils.load_urls(path)

    # load each JSON file from chaos.
    # Read each block of that file.
    # [P2] Sort the blocks by their size.
    # Also load the gold-text of that file.
    # If matching between gold-text and that element text is
    #   above a certain threshold, label that block as 1.
    # [P2] remove the matching part from gold-text.
    # Rewrite the blocks to another json file.

    # extract data from each url

    # load data
    pages = []
    domains = collections.defaultdict(lambda: 0)

    for id, url in enumerate(urls):
        if not url.strip():
            continue
        
        host = url.split('/', 3)[2]
        #if domains[host] > 2:
        #    continue
        domains[host] += 1
        print host

        page = utils.load_data(path, id)
        processor = processors.Processor([page], tokenizer=tokenizers.GenericTokenizer, analyzer=analyzers.LongestAnalyzer)
        features = processor.extract()

        clusterer = clusterers.DBSCAN()
        labels = clusterer.cluster(features).labels_

        clusters = collections.defaultdict(list)
        for text, label in zip(processor.texts, labels):
            clusters[int(label)].append(text)

        gold_text = utils.load_gold_text(path, id)
        gold_text = processor.tokenizer.tokenize(gold_text)

        max_score = 0
        best_label = None
        for label, texts in clusters.iteritems():
            tokens = ''
            for text in texts:
                tokens += text['tokens']
            score = processor.analyzer.get_similarity(tokens, gold_text)
            if score > max_score:
                max_score = score
                best_label = label

        for text in clusters[best_label]:
            text['label'] = 1


        page_texts = []
        for label, texts in clusters.iteritems():
            page_texts += texts
        random.shuffle(page_texts)
        pages.append(page_texts)

    #random.shuffle(pages)

    continuous_features = []
    discrete_features = []
    labels = []

    for page in pages:
        for text in page:
            text_length = len(text['tokens'])
            area = text['bound']['height'] * text['bound']['width']
            text_density = float(text_length) / float(area)

            # continuous_feature
            continuous_feature = [] #text_length, text_density]
            continuous_features.append(continuous_feature)

            # discrete features
            discrete_feature = dict()
            discrete_feature = dict(text['computed'].items())
            discrete_feature['path'] = ' > '.join(text['path'])
            """
            discrete_feature['selector'] = ' > '.join([
                '%s%s%s' % (
                    selector['name'],
                    '#' + selector['id'] if selector['id'] else '',
                    '.' + '.'.join(selector['classes']) if selector['classes'] else '',
                )
                for selector in text['selector']
            ])
            """
            discrete_feature['class'] = ' > '.join([
                '%s%s' % (
                    selector['name'],
                    '.' + '.'.join(selector['classes']) if selector['classes'] else '',
                )
                for selector in text['selector']
            ])
            """
            discrete_feature['id'] = ' > '.join([
                '%s%s' % (
                    selector['name'],
                    '#' + selector['id'] if selector['id'] else '',
                )
                for selector in text['selector']
            ])
            """
            discrete_features.append(discrete_feature)

            # label
            labels.append(text['label'])

    vectorizer = DictVectorizer()
    discrete_features = vectorizer.fit_transform(discrete_features).toarray()
    continuous_features = np.array(continuous_features)
    labels = np.array(labels).astype(np.float32)

    # scale features
    features = preprocessing.scale(features)

    features = np.hstack([continuous_features, discrete_features]).astype(np.float32)
    print features.shape

    precisions = []
    recalls = []
    f1scores = []
    supports = []

    rs = cross_validation.KFold(len(labels), n_folds=4, shuffle=False, random_state=0)
    for train_index, test_index in rs:
        print 'training size = %d, testing size = %d' % (len(train_index), len(test_index))

        clf = svm.SVC(verbose=False, kernel='linear', probability=False, random_state=0, cache_size=2000, class_weight='auto')
        clf.fit(features[train_index], labels[train_index])

        print clf.n_support_

        """
        negatives = []
        for i in clf.support_[:clf.n_support_[0]]:
            negatives.append(all_texts[i])

        positives = []
        for i in clf.support_[clf.n_support_[0]:]:
            positives.append(all_texts[i])

        stats(negatives, positives)
        """

        print "training:"
        predicted = clf.predict(features[train_index])
        print classification_report(labels[train_index], predicted)

        print "testing:"
        predicted = clf.predict(features[test_index])
        print classification_report(labels[test_index], predicted)

        precision, recall, f1score, support = precision_recall_fscore_support(labels[test_index], predicted)

        precisions.append(precision)
        recalls.append(recall)
        f1scores.append(f1score)
        supports.append(support)

    precisions = np.mean(np.array(precisions), axis=0)
    recalls = np.mean(np.array(recalls), axis=0)
    f1scores = np.mean(np.array(f1scores), axis=0)
    supports = np.mean(np.array(supports), axis=0)

    for label in range(2):
        print '%f\t%f\t%f\t%f' % (precisions[label], recalls[label], f1scores[label], supports[label])

    return

def stats(negatives, positives):
    negative_features = set()
    positives_features = set()
    negative_counts = collections.defaultdict(lambda: 0)
    positives_counts = collections.defaultdict(lambda: 0)

    for text in negatives:
        negative_features |= set(text['computed'].items())

    for text in positives:
        positives_features |= set(text['computed'].items())

    common = negative_features & positives_features

    for text in negatives:
        for key, value in text['computed'].iteritems():
            if (key, value) not in common:
                negative_counts[(key, value)] += 1

    for text in positives:
        for key, value in text['computed'].iteritems():
            if (key, value) not in common:
                positives_counts[(key, value)] += 1

    print 'negatives: '
    print list(reversed(sorted(filter(lambda x: x[1] > 1, negative_counts.items()), key=lambda pair: pair[1])))[:10]
    print 'positives: '
    print list(reversed(sorted(filter(lambda x: x[1] > 1, positives_counts.items()), key=lambda pair: pair[1])))[:10]


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Extract site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())