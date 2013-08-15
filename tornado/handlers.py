import tornado.web
import brukva.adisp
import logging
import settings
import simplejson as json
import urlparse
import tasks
import cPickle as pickle
import zlib

class Handler(tornado.web.RequestHandler):

    def cors(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header('Access-Control-Allow-Headers', '*')

class Redirect(Handler):

    def get(self, *args, **kwargs):
        self.redirect('http://ziyan.github.io/spider/')


class Capture(Handler):

    @tornado.web.asynchronous
    @brukva.adisp.process
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)

        # parse url and get site
        parts = urlparse.urlparse(data['url'])
        assert parts.scheme in ['http', 'https']
        site = '%s://%s' % (parts.scheme, parts.netloc)

        @brukva.adisp.async
        def process(site, data, callback):
            pipeline = settings.REDIS_ASYNC.pipeline()
            pipeline.hset('spider:pages:%s' % site, data['url'], zlib.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL)))
            pipeline.hlen('spider:pages:%s' % site)
            pipeline.get('spider:rules:%s' % site)
            pipeline.execute(callback)

        is_new, count, rules = yield process(site, data)

        # schedule learner
        if is_new and count > 1:
            tasks.learn.delay(site)

        self.cors()
        self.content_type = 'application/json'
        self.write(json.dumps({
            'is_new': is_new > 0,
            'count': count,
            'rules': json.loads(rules) if rules else None,
        }))
        self.finish()

    def head(self, *args, **kwargs):
        self.cors()
        self.finish()

class Site(Handler):

    @tornado.web.asynchronous
    @brukva.adisp.process
    def get(self, *args, **kwargs):
        url = self.get_argument('url')

        # parse url and get site
        parts = urlparse.urlparse(url)
        assert parts.scheme in ['http', 'https']
        site = '%s://%s' % (parts.scheme, parts.netloc)


        @brukva.adisp.async
        def process(site, data, callback):
            pipeline = settings.REDIS_ASYNC.pipeline()
            pipeline.hlen('spider:pages:%s' % site)
            pipeline.get('spider:rules:%s' % site)
            pipeline.execute(callback)

        pages_count, rules = yield process(site, data)

        @brukva.adisp.async
        def fetch(site, callback):
            settings.REDIS.get('spider:rules:%s' % site, callback)

        count, rules = yield fetch(site)

        self.cors()
        self.content_type = 'application/json'
        self.write(json.dumps({
            'count': count,
            'rules': json.loads(rules) if rules else None,
        }))
        self.finish()

    def head(self, *args, **kwargs):
        self.cors()
        self.finish()