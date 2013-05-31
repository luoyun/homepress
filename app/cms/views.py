# coding: utf-8

import os

from tornado.web import authenticated
from sqlalchemy.sql.expression import asc, desc, func

from yweb.handler import RequestHandler, has_permission
from yweb.utils.pagination import pagination

from ..auth.models import User
from .models import CMSCategory, CMSArticle


class CMSRequestHandler(RequestHandler):

    def initialize(self):
        self.view_kwargs = {
            'get_parents': self.get_parents,
            }

    def get_parents(self, category, include_myself=True):

        L = [ category ] if include_myself else []

        cur = category

        while True:
            if cur.parent_id:
                parent = self.db.query(CMSCategory).get( cur.parent_id )
                if parent:
                    L.insert(0, parent)
                    cur = parent
                    continue
            break

        return L


class ViewCategory(CMSRequestHandler):

    def get(self, ID):

        C = self.db.query(CMSCategory).get(ID)
        if not C:
            return self.write( _("Can not find category %s" % ID) )

        C.children = self.db.query(CMSCategory).filter_by(
            parent_id = C.id ).all()

        articles = self.db.query(CMSArticle).filter_by(
            category_id = C.id ).order_by(CMSArticle.id.desc()).all()
        #articles = C.articles

        d = { 'title': _("%s" % C.name),
              'category': C,
              'articles': articles }
        self.render('cms/category/view.html', **d)



class ViewArticle(CMSRequestHandler):

    def get(self, ID):

        A = self.db.query(CMSArticle).get(ID)
        if not A:
            return self.write( _("Can not find article %s" % ID) )

        category = A.category
        category.children = self.db.query(CMSCategory).filter_by(
            parent_id = category.id ).all()


        d = { 'title': _("%s" % A.name),
              'category': category,
              'article': A }

        self.render('cms/article/view.html', **d)


