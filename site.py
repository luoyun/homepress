#!/usr/bin/env python
# coding: utf-8

import os
import sys
import logging

import settings

# TODO: i18n is too ugly yet
#import gettext
#gettext.install( 'site', settings.I18N_PATH, unicode=False )
import __builtin__
__builtin__.__dict__['_'] = lambda s: s

import tornado.ioloop
import tornado.web

from yweb import orm
from yweb.handler import NotFoundHandler

import app.home.views as home_views
def get_handlers():

    handlers = []

    for m in settings.app:

        try:
            exec "from %s.urls import handlers as urls" % m
            handlers.extend(urls)
        except ImportError, e:
            logging.debug('import handlers from %s.urls failed: %s' % (m, e))

    handlers.extend([
            (r'/([^/ ]+)', home_views.GlobalEntry ),
            (r'/(.*)', NotFoundHandler)
            ])

    return handlers


from tornado.options import define, options
define("port", default=8888, help="given port", type=int)


tornado_settings = {
    'cookie_secret': 'MTMyNTMxxEwNDc3OC40MjA3NjgKCg==',
    'session_secret': 'gAJ9cQAoVjseiQZsb2NhbGVxAVUFemhfQ05xAl',
    'login_url': '/login',
    'no_permission_url': '/no_permission',
    'no_resource_url': '/no_resource',
    'static_path': settings.STATIC_PATH,
    'template_path': settings.TEMPLATE_PATH,
    'gzip': True,
#    'debug': True,

    'THEME': settings.THEME,
    'THEME_URL': settings.THEME_URL,
    'STATIC_URL': settings.STATIC_URL,
    'LANGUAGES': settings.LANGUAGES,
    }


class Application(tornado.web.Application):

    def __init__(self):

        # SQLAlchemy connect
        self.dbsession = orm.create_session()

        site_handlers = get_handlers()
        tornado.web.Application.__init__(self, site_handlers, **tornado_settings)



def main():
    reload(sys)
    sys.setdefaultencoding('utf8') 

    tornado.locale.load_gettext_translations(settings.I18N_PATH, "site")
    tornado.locale.set_default_locale('zh_CN')

    # options
    tornado.options.parse_command_line()

    logging.info("starting torando web server")

    # Start listen
    application = Application()
#    application.listen(options.port, xheaders=True)

    from tornado.httpserver import HTTPServer
    http_server = HTTPServer(application, xheaders=True)
    http_server.bind(options.port, '127.0.0.1')
    http_server.start(num_processes=0)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":

    try:
        main()
    finally:
        # TODO: dispose from db
        logging.info('Quit Now!')
