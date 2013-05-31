# coding: utf-8

import os, datetime, random, time, pickle, base64
from hashlib import sha1, md5

import tornado
from tornado.web import authenticated, asynchronous

from sqlalchemy.sql.expression import asc, desc

from yweb.contrib.session.models import Session
from yweb.handler import RequestHandler, has_permission
from yweb.utils.filesize import size as human_size

from .models import User
from .forms import LoginForm
from .utils import check_login_passwd as checkpass


class AccountRequestHandler(RequestHandler):

    def save_session(self, user_id):
        self.require_setting("cookie_secret", "secure cookies")

        session_key = sha1('%s%s' % (random.random(), time.time())).hexdigest()

        session_dict = {'user_id': user_id}
        sk = self.settings["session_secret"]
        pickled = pickle.dumps(session_dict, pickle.HIGHEST_PROTOCOL)
        pickled_md5 = md5(pickled + sk).hexdigest()
        session_data = base64.encodestring(pickled + pickled_md5)

        session = Session(session_key, session_data)
        self.db.add(session)
        self.db.commit()

        self.set_secure_cookie('session_key', session_key)


    def delete_session(self, user_id):
        session_key = self.get_secure_cookie('session_key')

        session = self.db.query(Session).filter_by(
            session_key = session_key).first()
        self.db.delete(session)
        self.db.commit()

        self.clear_all_cookies()



class Login(AccountRequestHandler):

    def prepare(self):
        self.d = { 'title': self.trans(_('Sign In')),
                   'next_url': self.get_argument('next', '/'),
                   'form': LoginForm(self) }

    def get(self):
        self.done()

    def post(self):
        _ = self.trans

        form = self.d['form']
        if form.validate():
            user = self.db.query(User).filter_by(username=form.username.data).first()
            if user:
                if user.is_locked:
                    form.password.errors.append( _('You have been lock.') )
                    return self.done()

                if checkpass(form.password.data, user.password):
                    self.save_session(user.id)
                    user.last_login = datetime.datetime.now()
                    self.db.commit()
                    return self.redirect(self.d['next_url'])
                else:
                    form.password.errors.append(_('Wrong password.'))
            else:
                form.username.errors.append(_('This user does not exist.'))

        self.done()

    def done(self):
        self.render('account/login.html', **self.d)



class Logout(AccountRequestHandler):

    @authenticated
    def get(self):
        if self.current_user:
            self.delete_session(self.current_user.id)
            self.redirect('/')
        else:
            d['username_error'] = 'Have not found user.'
            self.render('account/login.html', **d)
