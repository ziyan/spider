from settings import CELERY as celery
import settings
import utils
import clusterers
import processors
import cPickle as pickle
import simplejson as json
import zlib
import hashlib
import os

@celery.task(ignore_result=True)
def learn(site):

    # do we need to relearn?
    count = settings.REDIS_SYNC.hlen('spider:site:%s' % site)
    if settings.REDIS_SYNC.get('spider:site:%s:learned' % site) == count:
        return
    settings.REDIS_SYNC.set('spider:site:%s:learned' % site, count)

    print 'site = %s, count = %d' % (site, count)

    # load data from redis
    data = settings.REDIS_SYNC.hgetall('spider:site:%s' % site)
    data = [pickle.loads(zlib.decompress(data)) for data in data.values()]

    # process data
    processor = processors.Processor(data)
    features = processor.extract()

    # clustering
    clusterer = clusterers.DBSCAN()
    labels = clusterer.cluster(features).labels_

    # score
    clusters = processor.score(labels)

    # selecting selectors
    selectors = []
    for cluster in clusters:
        if cluster['confidence'] < settings.CONFIDENCE and cluster['score'] < settings.SCORE:
            continue
        for selector in cluster['selectors'].values():
            if selector[-1]['name'] != 'a':
                selectors.append(selector)

    selectors = ','.join(utils.consolidate_selectors(selectors).keys())
    settings.REDIS_SYNC.set('spider:site:%s:selectors' % site, selectors)
    print 'site = %s, selectors = %s' % (site, selectors)

    # for debugging purpose, write to file
    hash = hashlib.sha1(site).hexdigest()
    path = os.path.join(settings.STORE, hash[:2], hash)
    try:
        os.makedirs(path)
    except:
        pass
    path = os.path.join(path, 'clusters.json')
    with open(path, 'w') as f:
        f.write(json.dumps(clusters, indent=2, ensure_ascii=False).encode('utf8'))
    print 'site = %s, file = %s' % (site, path)