# coding: utf-8

import os, sys, base64, pickle, logging, struct, socket, re, datetime
import urllib, urlparse
import gettext
from hashlib import md5, sha512, sha1

import settings

import mako
from mako.exceptions import RichTraceback
import tornado

from mako.template import Template
from mako.lookup import TemplateLookup
mako.runtime.UNDEFINED = ''

from mako.exceptions import TemplateLookupException

from tornado.web import RequestHandler
from tornado import escape

from app.auth.models import User
from yweb.contrib.session.models import Session

from yweb import uimodule
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


from yweb.utils.ytime import htime, ftime
from yweb.utils.hstring import b2s

from app.language.models import Language
from app.site.models import SiteNav


class RequestHandler(RequestHandler):

    lookup = TemplateLookup([ settings.TEMPLATE_PATH ],
                            input_encoding="utf-8")

    title = _('Home')
    template_path = None

    def __init__(self, application, request, **kwargs):

        self.prepare_kwargs = {}

        super(RequestHandler, self).__init__(application, request, **kwargs)


    def render(self, template_name=None,
               return_string=False, **kwargs):
        """ Redefine the render """

        if not template_name:
            template_name = self.template_path

        t = self.lookup.get_template(template_name)

        # get entries
        L = self.db.query(Language.id).filter_by(
            codename = self.locale.code ).first()
        site_entries = self.db.query(SiteNav).filter_by(
            language_id = L.id ).order_by(SiteNav.position)

        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            xsrf_form_html=self.xsrf_form_html,
            xsrf_cookie=self.xsrf_cookie,
            reverse_url=self.application.reverse_url,

            static_url=self.static_url,
            theme_url=self.theme_url,

            LANGUAGES=self.settings['LANGUAGES'],

            #method
            htime = htime,
            ftime = ftime,
            has_permission = self.has_permission,
            e = uimodule.show_error,
            b2s = b2s,

            title = self.title,
            site_entries = site_entries,
        )

        args.update(kwargs)

        # We can set keyword with initialize() or prepare()
        args.update(self.prepare_kwargs)

        # We can define keyword in views with initialize()
        if hasattr(self, 'view_kwargs'):
            args.update(self.view_kwargs)

        # TODO: more readable bug track
        # http://docs.makotemplates.org/en/latest/usage.html#handling-exceptions
        try:
            html = t.render(**args)
        except:
            traceback = RichTraceback()
            html = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" href="/static/css/mako.css" />
    <title>LuoYun Mako Template System Trac Info</title>
  </head>
  <body>
    <h1>LuoYun Mako Template System Trac Info</h1>
    <pre>'''
            for (filename, lineno, function, line) in traceback.traceback:
                html += "File %s, line %s, in %s" % (filename, lineno, function)
                html += "%s\n" % line
            html += "%s: %s" % (str(traceback.error.__class__.__name__), traceback.error)
            html += "</pre></body></html>"

        if return_string: return html

        self.finish(html)


    def get_current_user(self):

        try:
            session = self.db.query(Session).filter_by(
                session_key = self.get_secure_cookie('session_key')).one()
        except MultipleResultsFound:
            logging.error( 'session: MultipleResultsFound, %s' %
                           self.get_secure_cookie('session_key') )
        except NoResultFound:
            return None

        # Does session expired ?
        if session.expire_date < datetime.datetime.now():
            return None

        sk = self.settings["session_secret"]
        encoded_data = base64.decodestring(session.session_data)
        pickled, tamper_check = encoded_data[:-32], encoded_data[-32:]
        if md5(pickled + sk).hexdigest() != tamper_check:
            # TODO
            logging.error("User tampered with session cookie.")
            return None
        try:
            session_dict = pickle.loads(pickled)
        except:
            session_dict = {}

        user = self.db.query(User).get(
            session_dict.get('user_id', 0) )

        if user:
            if user.is_locked: return None

            user.last_active = datetime.datetime.now()
            user.last_entry = self.request.uri

        return user



    def get_user_locale(self):
        user_locale = self.get_cookie("user_locale")

        if ( not user_locale and self.current_user ):
            user_locale = self.current_user.locale

        if user_locale:
            return tornado.locale.get(user_locale)
        else:
            # Use the Accept-Language header
            return None

    def has_permission(self, perm, user=None):

        if not user:
            user = self.current_user

        if not user:
            return False

#        for p in self.current_user.permissions:
#            if p.codename == perm or p.codename == 'admin':
#                return True

        for g in self.current_user.groups:
            for p in g.permissions:
                if p.codename == perm or p.codename == 'admin':
                    return True

        return False


    def theme_url(self, f):
        return self.static_url('theme/%s/%s' % (settings.THEME, f))

    def get_int(self, value, default=0):
        try:
            return int(value)
        except:
            return default

    def get_argument_int(self, key, default=0):
        value = self.get_argument(key, default)
        try:
            return int(value)
        except:
            return default

    def urlupdate(self, params):
        ''' params is a dict: { 'key': value } '''

        new = []

        if '?' in self.request.uri:
            path, oldparams = self.request.uri.split('?')
            update_keys = params.keys()

            for k, v in urlparse.parse_qsl( oldparams ):
                if k in update_keys:
                    v = params[k]
                    del params[k]
                new.append( (k, v) )
        else:
            path = self.request.uri

        if params:
            for k in params.keys():
                new.append( (k, params[k]) )

        return '?'.join([path, urllib.urlencode( new )])


    def xsrf_isok(self):
        token = (self.get_argument("_xsrf", None) or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken"))
        if not token:
            return _("'_xsrf' argument missing")
        if self.xsrf_token != token:
            return _("XSRF cookie does not match")

    @property
    def xsrf_cookie(self):
        return escape.xhtml_escape(self.xsrf_token)

    def trans(self, s):
        return self.locale.translate(s)

    def get_no_permission_url(self):
        self.require_setting("no_permission_url", "@has_permission")
        return self.application.settings["no_permission_url"]

    def get_template_by_locale(self, path):

        p = os.path.join(settings.TEMPLATE_PATH, path.lstrip('/'))
        f = '%s.html' % self.locale.code
        if os.path.exists( os.path.join(p, f) ):
            return os.path.join(path, f)
        else:
            f = 'default.html'
            if os.path.exists( os.path.join(p, 'default.html') ):
                return os.path.join(path, f)
        return None

    @property
    def db(self):
        return self.application.dbsession()

    def on_finish(self):
        self.application.dbsession.remove()


import functools, urlparse, urllib
def has_permission(codename):
    """ Needed permission 'codename'. """
    def foo(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                if self.request.method in ("GET", "HEAD"):
                    url = self.get_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = self.request.full_url()
                        else:
                            next_url = self.request.uri
                            url += "?" + urllib.urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
                raise HTTPError(403)

            # User is authenticated
#            for p in self.current_user.permissions:
#                if p.codename == codename or p.codename == 'admin':
#                    return method(self, *args, **kwargs)

            for g in self.current_user.groups:
                for p in g.permissions:
                    if p.codename == codename or p.codename == 'admin':
                        return method(self, *args, **kwargs)

            #raise HTTPError(403, 'Need permission "%s"', codename)
            url = self.get_no_permission_url()
            url += "?codenames=%s" % codename
            return self.redirect( url )

        return wrapper
    return foo





class NotFoundHandler(RequestHandler):

    def prepare(self):
        try:
            self.set_status(404)
            self.render('/404.html')
        except TemplateLookupException, e:
            self.send_error(500)
