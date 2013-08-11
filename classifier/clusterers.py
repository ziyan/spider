from sklearn import cluster
from sklearn.preprocessing import StandardScaler
import numpy as np

class DBSCAN(object):

    def cluster(self, data):
        data = StandardScaler().fit_transform(data)
        db = cluster.DBSCAN().fit(data)
        return db

class AffinityPropagation(object):
    def cluster(self, data):
        af = cluster.AffinityPropagation().fit(data)
        return af