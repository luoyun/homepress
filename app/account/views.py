# coding: utf-8

import os, datetime, random, time
from hashlib import sha1

import tornado
from sqlalchemy.sql.expression import asc, desc

from ..auth.models import User
from ..auth.views import AccountRequestHandler
from ..auth.utils import enc_login_passwd

from .models import ResetPasswordApply
from .forms import ResetPasswordForm, ResetPasswordApplyForm

from yweb.handler import RequestHandler, has_permission


from yweb.utils.mail import sendmail


class Index(AccountRequestHandler):

    def get(self):
        self.render('account/index.html')


class ResetPassword(AccountRequestHandler):

    def prepare(self):
        key = self.get_argument('key', None)

        E = []
        if key:
            title = self.trans(_('Reset my password.'))
            form = ResetPasswordForm(self)
            template = 'account/reset_password.html'
            ar = self.db.query(ResetPasswordApply).filter_by(key=key).first()
            if not ar:
                E.append(self.trans(_('Invalid key.')))
        else:
            title = self.trans(_('Reset my password.'))
            form = ResetPasswordApplyForm(self)
            template = 'account/reset_password_apply.html'

        self.d = { 'title': title, 'form': form, 'E': E }
        self.key = key
        
        method = self.request.method.lower()

        if method == 'get':
            self.render(template, **self.d)

        elif method == 'post':
            self.template = template
            if key:
                self.ar = ar
                self.post_reset()
            else:
                self.post_apply()


    def post_apply(self):

        form = self.d['form']
        if form.validate():
            u = self.db.query(User).filter_by(
                email = form.email.data ).first()
            if u:
                au = self.db.query(ResetPasswordApply).filter_by(
                    user_id = u.id ).first()
                if au:
                    au.key = sha1(str(random.random())).hexdigest()
                else:
                    au = ResetPasswordApply(u)
                    self.db.add(au)

                self.db.commit()
                # TODO: sendmail to user
                self.sendmail(au)

                self.template = 'account/reset_password_apply_success.html'
            else:
                form.email.errors.append(self.trans(_('This email does not register now.')))

        self.render(self.template, **self.d)


    def post_reset(self):
        form = self.d['form']
        user = self.ar.user if self.ar else None
        if form.validate() and user:
            user.password = enc_login_passwd(form.password.data)
            self.db.delete(self.ar)
            self.db.commit()
            self.save_session(user.id)
            next_url = self.get_argument('next', '/')
            return self.redirect(next_url)

        self.render('account/reset_password.html', **self.d)


    def sendmail(self, _apply):
        url = 'http://www.luoyun.co' + self.reverse_url('account:reset_password') + '?key=%s' % _apply.key
        d = { 'return_string': True, 'APPLY': _apply,
              'RESET_PASSWORD_URL': url }
        body = self.render('account/reset_password_email.html', **d)
        sendmail( [_apply.user.email],
                  _('Reset password for LuoYun.CO.'),
                  body, bcc = ['admin@luoyun.co'] )


