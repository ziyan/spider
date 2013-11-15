import collections
import math
import numpy as np
import mlpy

class TermFrequencyAnalyzer(object):

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


class LongestAnalyzer(object):

    def __init__(self, *documents):
        pass

    def get_similarity(self, a, b):
        #return self.lcs(a, b)

        a = np.array(list(a), dtype='U1').view(np.uint32)
        b = np.array(list(b), dtype='U1').view(np.uint32)
        length, path = mlpy.lcs_std(a, b)
        return length
        
    def lcs(self, a, b):
        a = a[:200]
        b = b[:200]
        if (len(a) < len(b)):
            a, b = b, a

        M = len(a)
        N = len(b)

        arr = np.zeros((2, N + 1))
        for i in range(1, M + 1):
            curIdx = i % 2
            prevIdx = 1 - curIdx
            ai = a[i - 1]
            for j in range(1, N + 1):
                bj = b[j - 1]
                if (ai == bj):
                    arr[curIdx][j] = 1 + arr[prevIdx][j - 1]
                else:
                    arr[curIdx][j] = max(arr[curIdx][j - 1], arr[prevIdx][j])

        return arr[M % 2][N]
