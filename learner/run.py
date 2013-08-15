#!/usr/bin/env python

import clusterers
import preprocessors
import analyzers
import tokenizers
import simplejson as json
import collections
import os
import argparse
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

def main(args):

    path = get_data_path(args.site[0])
    urls = load_urls(path)

    # load data
    data = []
    for id, url in enumerate(urls):
        data.append(load_data(path, id))

    # text analyzer
    pages = []
    tokenizer = tokenizers.EnglishTokenizer()
    for document in data:
        texts = document['titles'] + document['descriptions']
        for node in document['texts']:
            texts += node['text']
        tokens = tokenizer.tokenize(*texts)
        pages.append(tokens)
    analyzer = analyzers.TextAnalyzer(*pages)

    # process data
    preprocessor = preprocessors.Preprocessor(data)
    pages_ids, texts_ids, features = preprocessor.extract()

    # clustering
    clusterer = clusterers.DBSCAN()
    clusters = collections.defaultdict(list)
    for id, label in enumerate(clusterer.cluster(features).labels_):
        cluster_id = int(label)
        clusters[cluster_id].append(id)

    results = dict()

    # score each cluster    
    for cluster_id, ids in clusters.iteritems():
        # correlate the datapoint back to the page and text block
        html = []
        pages = collections.defaultdict(list)
        for id in ids:
            page_id = pages_ids[id]
            text_id = texts_ids[id]
            html.append(data[page_id]['texts'][text_id]['html'])
            tokens = tokenizer.tokenize(*data[page_id]['texts'][text_id]['text'])
            pages[page_id].append(tokens)

        # also find the page title and description
        hints = collections.defaultdict(list)
        for page_id in pages.keys():
            hints[page_id] += tokenizer.tokenize(*data[page_id]['titles'])
            hints[page_id] += tokenizer.tokenize(*data[page_id]['descriptions'])

        # score similarity within each page
        scores = dict()
        for page_id, strings in pages.iteritems():
            
            # topic score based on hints
            if hints[page_id]:
                topic_score = 0.0
                for tokens in strings:
                    topic_score += analyzer.get_similarity(hints[page_id], tokens)
            else:
                topic_score = 1.0

            # coherent score
            if strings:
                coherent_score = 0.0
                for tokens1, tokens2 in itertools.product(strings, repeat=2):
                    if tokens1 == tokens2:
                        continue
                    coherent_score += analyzer.get_similarity(tokens1, tokens2)
            else:
                coherent_score = 1.0

            scores[page_id] = topic_score * coherent_score

        if sum(scores.values()) <= 0:
            continue

        results[cluster_id] = {
            'scores': scores,
            'average': sum(scores.values()) / len(pages),
            'html': html,
        }


    output = json.dumps(results, indent=2, ensure_ascii=False)
    print output.encode('utf8')

def parse_args():
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description='Run the whole pipeline on site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
