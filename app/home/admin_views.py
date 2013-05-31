# coding: utf-8

from yweb.handler import RequestHandler, has_permission

from ..language.models import Language

class Index(RequestHandler):

    @has_permission('admin')
    def get(self):
        self.render('admin/index.html')
