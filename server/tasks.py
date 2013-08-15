from settings import CELERY as celery


@celery.task(ignore_result=True)
def learn(site):
    print 'Learning %s ...' % site
