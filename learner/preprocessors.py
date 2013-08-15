from sklearn.feature_extraction import DictVectorizer
import numpy as np
import hashlib

class Preprocessor(object):

    CONTINUOUS_FEATURES = {
        'width': lambda page, datapoint: float(datapoint['bound']['width']),
    }

    def __init__(self, data):
        self.data = data

    def extract(self):

        pages_ids = []
        texts_ids = []

        continuous_features = []
        discrete_features = []

        for page_id, page in enumerate(self.data):
            for text_id, text in enumerate(page['texts']):
                pages_ids.append(page_id)
                texts_ids.append(text_id)

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

        features = np.hstack([continuous_features, discrete_features]).astype(np.float32)
        return pages_ids, texts_ids, features
