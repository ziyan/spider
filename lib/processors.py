from sklearn.feature_extraction import DictVectorizer
import numpy as np
import tokenizers
import analyzers
import collections
import itertools

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
                discrete_feature['path'] = text['path']
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
            )),
        ))

        for page, text, label in zip(self.pages, self.texts, labels):

            hints = page['titles'] + page['descriptions']
            relevance_score = self.analyzer.get_similarity(text['text'], hints) if hints else 1.0

            cluster = clusters[int(label)]
            cluster['selectors'].append(text['selector'])
            cluster['pages'][page['url']]['score'] += relevance_score
            cluster['pages'][page['url']]['texts'].append(text['text'])

        for cluster in clusters.values():
            cluster['selectors'] = '' #set(cluster['selectors'])
            for page in cluster['pages'].values():
                coherent_score = 0.0
                for text1, text2 in itertools.product(page['texts'], repeat=2):
                    if text1 is not text2:
                        coherent_score += self.analyzer.get_similarity(text1, text2)
                del page['texts']
                page['score'] *= coherent_score
                cluster['score'] += page['score']

        for label in clusters.keys():
            if clusters[label]['score'] <= 0:
                del clusters[label]

        return clusters

