# coding: utf-8

import logging
import os, datetime, random, time
from hashlib import sha1

import tornado
from tornado.web import authenticated, asynchronous

from ..auth.models import User
from ..auth.views import AccountRequestHandler
from ..auth.utils import enc_login_passwd

from .models import RegistrationApply
from .forms import RegistrationApplyForm, RegistrationForm

from yweb.handler import RequestHandler
from yweb.utils.mail import sendmail


class RegisterApply(RequestHandler):

    def get(self):
        form = RegistrationApplyForm(self)
        d = { 'title': _('Registration Apply'),
              'form': form }
        self.render("registration/apply.html", **d)

    def post(self):

        form = RegistrationApplyForm(self)
        form.email.data = self.get_argument('email', '')
        form.accept_rules.data = self.get_argument('accept_rules', 0)

        if form.validate():
            print 'validate()'
        else:
            print 'form failed: ', form.email.errors

        print 'self.request = ', self.request

class Register(AccountRequestHandler):

    def prepare(self):

        key = self.get_argument('key', None)
        E = []

        if key:
            form = RegistrationForm(self)
            title = _('Complete the registration')
            template = "registration/registration.html"
            # check key
            x=self.db.query(RegistrationApply).filter_by(key=key).first()
            if x:
                self.exist_key = x
            else:
                E.append( _('key "%s"is not exist.') % key)

        else:
            form = RegistrationApplyForm(self)
            title = _('Registration Apply')
            template = "registration/apply.html"

        d = { 'form': form, 'title': title, 'E': E }

        if self.request.method.lower() == 'get' or E:
             return self.render(template, **d)

        self.d = d
        self.key = key
        self.template = template


    def post(self):

        if self.key:
            self.post_registration()
        else:
            self.post_apply()


    def post_apply(self):

        form = self.d['form']

        while True:
            if not form.validate(): break

            # check email
            K=self.db.query(RegistrationApply).filter_by(email=form.email.data).first()
            U=self.db.query(User).filter_by(email=form.email.data).first()
            if K:
                K.key = sha1(str(random.random())).hexdigest()
            elif U:
                form.email.errors.append( _('Email (%s) is alreay exist.') % form.email.data )
                break
            else:
                K = RegistrationApply(email = form.email.data)
                self.db.add(K)

            self.db.commit()
            # TODO: sendmail
            logging.info('prepare to sendmail to %s' % K.email)
            self.sendmail(K)
            return self.render('registration/apply_complete.html', **self.d)

        self.render(self.template, **self.d)


    def post_registration(self):

        form = self.d['form']

        if form.validate():
            old = self.db.query(User).filter_by(username=form.username.data).count()
            if old:
                form.username.errors.append( _('Username is occupied.'))
            else:
                encpass = enc_login_passwd(form.password.data)
                new = User( username = form.username.data,
                            password = encpass )
                new.email = self.exist_key.email
                self.db.add(new)
                self.db.delete(self.exist_key)
                self.db.commit()
                self.save_session(new.id)
                return self.redirect('/')

        self.render(self.template, **self.d)


    def sendmail(self, _apply):
        url = 'http://www.luoyun.co/register?key=%s' % _apply.key
        d = { 'return_string': True, 'APPLY': _apply,
              'REGISTER_URL': url }
        body = self.render('registration/apply_email.html', **d)
        sendmail( [_apply.email],
                  _('Thanks for register LuoYun.CO'),
                  body, bcc = ['lijian@luoyun.co'] )
