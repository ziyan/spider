from sklearn import cluster
from sklearn.preprocessing import StandardScaler

class DBSCAN(object):

    def cluster(self, data):
        data = StandardScaler().fit_transform(data)
        db = cluster.DBSCAN(eps=0.5, min_samples=5).fit(data)
        return db
