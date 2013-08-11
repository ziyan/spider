from sklearn.feature_extraction import DictVectorizer
import numpy as np
import hashlib

class Preprocessor(object):

    CONTINUOUS_FEATURES = {
        #'bound_height': lambda page, datapoint: datapoint['bound']['height'],
        #'bound_width': lambda page, datapoint: datapoint['bound']['width'],
        #'bound_top': lambda page, datapoint: datapoint['bound']['top'],
        #'bound_left': lambda page, datapoint: datapoint['bound']['left'],
        #'bound_bottom': lambda page, datapoint: page['body']['bound']['height'] - datapoint['bound']['top'],
        #'bound_right': lambda page, datapoint: page['body']['bound']['width'] - datapoint['bound']['left'],
        #'text_length': lambda page, datapoint: len(' '.join([text.strip() for text in datapoint['text']])),
        #'text_count': lambda page, datapoint: len(datapoint['text']),
    }

    def __init__(self, data):
        self.data = data

    def extract(self):

        datapoints = []

        continuous_features = []
        discrete_features = []

        for page in self.data:
            for datapoint in page['texts']:
                datapoints.append(datapoint)

                # continuous features
                continuous_features.append([
                    process(page, datapoint)
                    for key, process in self.CONTINUOUS_FEATURES.iteritems()
                ])

                # discrete features
                discrete_feature = dict(datapoint['computed'].items())
                #discrete_feature['path'] = datapoint['path']
                #discrete_feature['element'] = datapoint['element']
                discrete_features.append(discrete_feature)

        # build numpy array
        continuous_features = np.array(continuous_features)

        # vectorize discrete features
        vectorizer = DictVectorizer()
        discrete_features = vectorizer.fit_transform(discrete_features).toarray()

        features = np.hstack([continuous_features, discrete_features]).astype(np.float32)
        return datapoints, features
