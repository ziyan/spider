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
        site = '%s://%s' % (parts.scheme.lower(), parts.netloc.lower())

        @brukva.adisp.async
        def process(site, data, callback):
            pipeline = settings.REDIS_ASYNC.pipeline()
            pipeline.exists('spider:site:%s' % site)
            pipeline.hset('spider:site:%s' % site, data['url'], zlib.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL)))
            pipeline.hlen('spider:site:%s' % site)
            pipeline.get('spider:site:%s:selectors' % site)
            pipeline.execute(callback)

        is_old_site, is_new_page, count, selectors = yield process(site, data)

        # stats
        settings.REDIS_ASYNC.incr('spider:stats:usage')
        if not is_old_site:
            settings.REDIS_ASYNC.incr('spider:stats:sites')
        if is_new_page:
            settings.REDIS_ASYNC.incr('spider:stats:pages')

        # schedule learner
        if is_new_page and count > 1:
            tasks.learn.delay(site)

        self.cors()
        self.content_type = 'application/json'
        self.write(json.dumps({
            'is_new_site': not is_old_site,
            'is_new_page': is_new_page > 0,
            'count': count,
            'selectors': selectors,
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
        def process(site, callback):
            pipeline = settings.REDIS_ASYNC.pipeline()
            pipeline.hlen('spider:site:%s' % site)
            pipeline.get('spider:site:%s:selectors' % site)
            pipeline.execute(callback)

        count, selectors = yield process(site)

        self.cors()
        self.content_type = 'application/json'
        self.write(json.dumps({
            'count': count,
            'selectors': selectors,
        }))
        self.finish()

    def head(self, *args, **kwargs):
        self.cors()
        self.finish()


class Stats(Handler):

    @tornado.web.asynchronous
    @brukva.adisp.process
    def get(self, *args, **kwargs):

        @brukva.adisp.async
        def process(callback):
            pipeline = settings.REDIS_ASYNC.pipeline()
            pipeline.get('spider:stats:usage')
            pipeline.get('spider:stats:sites')
            pipeline.get('spider:stats:pages')
            pipeline.execute(callback)

        usage, sites, pages = yield process()

        self.cors()
        self.content_type = 'application/json'
        self.write(json.dumps({
            'usage': usage,
            'sites': sites,
            'pages': pages,
        }))
        self.finish()

    def head(self, *args, **kwargs):
        self.cors()
        self.finish()