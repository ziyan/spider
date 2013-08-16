from sklearn.feature_extraction import DictVectorizer
import numpy as np
import tokenizers
import analyzers
import collections
import itertools
import utils

class Processor(object):

    CONTINUOUS_FEATURES = {
        'width': lambda page, datapoint: float(datapoint['bound']['width']),
    }

    def __init__(self, data):
        self.data = data
        self.tokenize()

    def tokenize(self):
        self.tokenizer = tokenizers.EnglishTokenizer()

        # tokenize data fields in each page
        pages = []
        for page in self.data:
            page['titles'] = self.tokenizer.tokenize(*page['titles'])
            page['descriptions'] = self.tokenizer.tokenize(*page['descriptions'])
            tokens = page['titles'] + page['descriptions']
            for text in page['texts']:
                text['text'] = self.tokenizer.tokenize(*text['text'])
                tokens += text['text']
            pages.append(tokens)

        self.analyzer = analyzers.TextAnalyzer(*pages)

    def extract(self):

        self.pages = []
        self.texts = []

        continuous_features = []
        discrete_features = []


        for page in self.data:
            for text in page['texts']:

                # keep track of corresponding page and text for each datapoint
                self.pages.append(page)
                self.texts.append(text)

                # continuous features
                continuous_features.append([
                    process(page, text)
                    for key, process in self.CONTINUOUS_FEATURES.iteritems()
                ])

                # discrete features
                discrete_feature = dict(text['computed'].items())
                discrete_feature['path'] = ' > '.join(text['path'])
                discrete_features.append(discrete_feature)

        # build numpy array
        continuous_features = np.array(continuous_features)

        # vectorize discrete features
        vectorizer = DictVectorizer()
        discrete_features = vectorizer.fit_transform(discrete_features).toarray()

        return np.hstack([continuous_features, discrete_features]).astype(np.float32)

    def score(self, labels):

        clusters = collections.defaultdict(lambda: dict(
            score=0.0,
            selectors=[],
            pages=collections.defaultdict(lambda: dict(
                score=0.0,
                texts=[],
                htmls=[],
            )),
        ))

        for page, text, label in zip(self.pages, self.texts, labels):

            hints = page['titles'] + page['descriptions']
            relevance_score = self.analyzer.get_similarity(text['text'], hints) if hints else 1.0

            cluster = clusters[int(label)]
            cluster['selectors'].append(text['selector'])
            cluster['pages'][page['url']]['score'] += relevance_score
            cluster['pages'][page['url']]['texts'].append(text['text'])
            cluster['pages'][page['url']]['htmls'].append(text['html'])

        for cluster in clusters.values():

            # count non zero pages
            count = 0

            # coherence score
            for page in cluster['pages'].values():
                coherent_score = 0.0
                for text1, text2 in itertools.product(page['texts'], repeat=2):
                    if text1 is not text2:
                        coherent_score += self.analyzer.get_similarity(text1, text2)
                del page['texts']

                # combine scores
                page['score'] *= coherent_score
                cluster['score'] += page['score']

                if page['score'] > 0:
                    count += 1

            if count > 0: cluster['score'] /= float(count)
            cluster['confidence'] = float(count) / float(len(cluster['pages']))

            # consolidate clusters
            cluster['selectors'] = utils.consolidate_selectors(cluster['selectors'])

        # get rid of the clusters with score 0
        #for label in clusters.keys():
        #    if clusters[label]['score'] <= 0 or clusters[label]['confidence'] <= 0:
        #        del clusters[label]

        return clusters.values()


