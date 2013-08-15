#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import settings

application = tornado.web.Application([
    (r'/', 'handlers.Redirect'),
    (r'/capture', 'handlers.Capture'),
    (r'/site', 'handlers.Site'),
])

if __name__ == '__main__':    
    application.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()
