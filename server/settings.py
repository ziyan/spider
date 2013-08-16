
import os
import sys

lib_path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))
if lib_path not in sys.path:
    sys.path[0:0] = [lib_path]

PORT = 9090

import redis
REDIS_SYNC = redis.StrictRedis(db=0)

import brukva
REDIS_ASYNC = brukva.Client(selected_db=0)

import celery
CELERY = celery.Celery('spider', broker='redis://localhost:6379/0')

STORE = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'store'))


CONFIDENCE = 0.5
SCORE = 20.0
