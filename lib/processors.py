from sklearn.feature_extraction import DictVectorizer
import numpy as np
import tokenizers
import analyzers
import collections
import itertools
import utils
import re

class Processor(object):

    CONTINUOUS_FEATURES = {
        'width': lambda page, datapoint: float(datapoint['bound']['width']),
    }

    def __init__(
        self,
        data,
        tokenizer=tokenizers.EnglishTokenizer,
        analyzer=analyzers.TermFrequencyAnalyzer
    ):
        self.data = data
        self.tokenizer = tokenizer()

        # tokenize data fields in each page
        pages = []
        for page in self.data:
            page['titles'] = self.tokenizer.tokenize(*page['titles'])
            page['descriptions'] = self.tokenizer.tokenize(*page['descriptions'])
            tokens = page['titles'] + page['descriptions']
            for text in page['texts']:
                text['tokens'] = self.tokenizer.tokenize(*text['text'])
                tokens += text['tokens']
            pages.append(tokens)

        self.analyzer = analyzer(*pages)

    def extract(self):
        """
        Extract features for clustering
        """

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

    def prepare(self, labels):
        """
        Prepare SVM training data.
        """

        pages = collections.defaultdict(lambda: collections.defaultdict(lambda: dict(
            score=0.0,
            selectors=[],
            tokens=[],
            text=[],
            discrete={},
            continuous=[],
            label=0,
        )))

        for page, text, label in zip(self.pages, self.texts, labels):

            hints = page['titles'] + page['descriptions']
            relevance_score = self.analyzer.get_similarity(text['tokens'], hints) if hints else 0.0

            cluster = pages[page['url']][int(label)]
            # cluster['selectors'].append(text['selector'])
            cluster['score'] += relevance_score
            cluster['tokens'].append(text['tokens'])
            cluster['text'] += text['text']

            # collect discrete features
            cluster['discrete'].update(text['computed'].items())
            cluster['discrete']['path'] = ' > '.join(text['path'])

        continuous_features = []
        discrete_features = []
        labels = []

        # for each page, find the best cluster and label it 1
        for url, clusters in pages.iteritems():
            cluster = max(clusters.values(), key=lambda x: x['score'])
            cluster['label'] = 1

            for cluster in clusters.values():
                discrete_features.append(cluster['discrete'])
                continuous_features.append(cluster['continuous'])
                labels.append(cluster['label'])

        # build numpy array
        continuous_features = np.array(continuous_features)
        labels = np.array(labels)

        # vectorize discrete features
        vectorizer = DictVectorizer()
        discrete_features = vectorizer.fit_transform(discrete_features).toarray()

        return pages, np.hstack([continuous_features, discrete_features]).astype(np.float32), labels.astype(np.float32)


    def score(self, labels):

        clusters = collections.defaultdict(lambda: dict(
            score=0.0,
            selectors=[],
            pages=collections.defaultdict(lambda: dict(
                score=0.0,
                tokens=[],
                text=[],
            )),
        ))

        for page, text, label in zip(self.pages, self.texts, labels):

            hints = page['titles'] + page['descriptions']
            relevance_score = self.analyzer.get_similarity(text['tokens'], hints) if hints else 1.0

            cluster = clusters[int(label)]
            cluster['selectors'].append(text['selector'])
            cluster['pages'][page['url']]['score'] += relevance_score
            cluster['pages'][page['url']]['tokens'].append(text['tokens'])
            cluster['pages'][page['url']]['text'] += text['text']

        for cluster in clusters.values():

            # count non zero pages
            count = 0

            # coherence score
            for page in cluster['pages'].values():
                coherent_score = 0.0
                for tokens1, tokens2 in itertools.product(page['tokens'], repeat=2):
                    if tokens1 is not tokens2:
                        coherent_score += self.analyzer.get_similarity(tokens1, tokens2)
                if len(page['tokens']) <= 1:
                    coherent_score = 1.0
                del page['tokens']

                # combine scores
                page['score'] *= coherent_score
                cluster['score'] += page['score']

                if page['score'] > 0:
                    count += 1

                # normalize content
                #page['content'] = re.sub(r'[^a-zA-Z0-9]+', ' ', page['text'])
                #page['content'] = re.sub(r'[\s]{2,}', ' ', page['text']).strip()

            if count > 0: cluster['score'] /= float(count)
            cluster['confidence'] = float(count) / float(len(cluster['pages']))

            # consolidate clusters
            cluster['selectors'] = utils.consolidate_selectors(cluster['selectors'])

        # get rid of the clusters with score 0
        for label in clusters.keys():
            if clusters[label]['score'] <= 0 or clusters[label]['confidence'] <= 0:
                del clusters[label]

        return clusters.values()


