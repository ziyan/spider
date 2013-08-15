
PORT = 9090

import redis
REDIS_SYNC = redis.StrictRedis(db=0)

import brukva
REDIS_ASYNC = brukva.Client(selected_db=0)

import celery
CELERY = celery.Celery('spider', broker='redis://localhost:6379/0')

