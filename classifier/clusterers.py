from sklearn import cluster

class DBSCAN(object):

    def cluster(self, data):
        db = cluster.DBSCAN(eps=0.5, min_samples=5).fit(data)
        core_samples = db.core_sample_indices_
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        return db
