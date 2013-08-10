import numpy as np

class Preprocessor(object):

    TEXT_PROCESSORS = {
        'bound_height': lambda data, text: text['bound']['height'],
        'bound_width': lambda data, text: text['bound']['width'],
        'bound_top': lambda data, text: text['bound']['top'],
        'bound_left': lambda data, text: text['bound']['left'],
        'bound_bottom': lambda data, text: data['body']['bound']['height'] - text['bound']['top'],
        'bound_right': lambda data, text: data['body']['bound']['width'] - text['bound']['left'],
        'text_length': lambda data, text: len((''.join(text['text'])).split()),
        'text_count': lambda data, text: len(text['text']),
        'path_length': lambda data, text: len(text['path']),
    }


    def __init__(self, data):
        self.data = data

    def process_texts(self):
        data = []
        texts = self.data['texts']
        for text in texts:
            data.append([
                process(self.data, text)
                for key, process in self.TEXT_PROCESSORS.iteritems()
            ])
        data = np.array(data).astype(np.float32)
        return texts, data
