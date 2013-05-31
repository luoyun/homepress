# coding: utf-8

from yweb.handler import RequestHandler
from sqlalchemy import and_

from ..site.models import SiteEntry, SiteArticle
from ..language.models import Language


class Index(RequestHandler):

    def get(self):

        E = self.db.query(SiteEntry).filter_by(slug='home').first()
        L = self.db.query(Language).filter_by(
            codename = self.locale.code ).first()
        if E and L:
            A = self.db.query(SiteArticle).filter(
                and_( SiteArticle.entry_id == E.id,
                      SiteArticle.language_id == L.id ) ).first()
        else: A = None

        if A:
            d = {'mainbody': A.body_html}
        else:
            d = {'mainbody': _('Please set the site article for entry "home" first.') }

        self.render('home/index.html', **d)


class GlobalEntry(RequestHandler):

    title = _("Global Entry")

    def get(self, slug):

        entry = self.db.query(SiteEntry).filter_by(slug=slug).first()

        if not entry:
            return self.send_error(404)

        select_language = self.get_argument('language', None)
        if select_language:
            cur_language = self.db.query(Language).filter_by(
                codename = select_language ).first()
        else:
            cur_language = self.db.query(Language).filter_by(
                codename = self.locale.code ).first()

        article = self.db.query(SiteArticle).filter_by(
            entry_id = entry.id ).filter_by(
            language_id = cur_language.id).first()

        d = { 'entry': entry, 'article': article,
              'cur_language': cur_language }
        if article:
            d['title'] = article.name
            AL = []
        else:
            d['title'] = _('Not support your language.')
            AL = self.db.query(SiteArticle).filter_by(
                entry_id = entry.id ).all()

        d['available_article_list'] = AL

        self.render('home/global_entry.html', **d)


class NoPermission(RequestHandler):

    def get(self):

        cs = self.get_argument('codenames', '')
        self.render('home/no_permission.html', codenames = cs)


class SetLocale(RequestHandler):

    def get(self):

        user_locale = self.get_argument("language", self.locale.code)
        next_url = self.get_argument("next", '/')
        self.set_cookie("user_locale", user_locale)
        self.redirect(next_url)
