import collections
import math


class TextAnalyzer(object):

    def __init__(self, *documents):
        self.idf = self.compute_idf(*documents)

    def compute_idf(self, *documents):

        # document frequency
        df = collections.defaultdict(int)
        for tokens in documents:
            for token in set(tokens):
                df[token] += 1

        # idf
        idf = dict()
        for token, count in df.iteritems():
            idf[token] = math.log(float(len(documents)) / float(count))

        return idf

    def get_similarity(self, *strings):
        if len(strings) <= 1:
            return 0.0

        counts = [collections.defaultdict(int) for _ in strings]

        for index, tokens in enumerate(strings):
            for token in tokens:
                counts[index][token] += 1

        score = 0.0

        # intercept of the tokens
        for token in set.intersection(*[set(tokens) for tokens in strings]):
            # term frequency
            tf = float(sum([count[token] for count in counts]))
            score += tf * self.idf[token]

        return score
