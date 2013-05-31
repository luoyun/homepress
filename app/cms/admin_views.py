# coding: utf-8

import os
import json

from tornado.web import authenticated
from sqlalchemy.sql.expression import asc, desc, func

from yweb.handler import RequestHandler, has_permission
from yweb.utils.pagination import pagination

from ..auth.models import User
from .models import CMSCategory, CMSArticle
from .forms import CategoryForm, ArticleForm


class CategoryRequestHandler(RequestHandler):

    def initialize(self):
        categories = self.db.query(CMSCategory).filter_by(
            parent_id = None ).all()

        for C in categories:
            C.children = self.db.query(CMSCategory).filter_by(
                parent_id = C.id ).all()

        self.view_kwargs = {
            'categories': categories,
            }

class Index(CategoryRequestHandler):

    title = _('CMS Home')

    @has_permission('admin')
    def get(self):

        self.render('admin/cms/index.html')


class CategoryIndex(CategoryRequestHandler):

    title = _('Manager Category')

    @has_permission('admin')
    def get(self):

        category_list = self.db.query(CMSCategory).all()

        d = {'category_list': category_list}
        self.render('admin/cms/category.html', **d)


class ViewCategory(CategoryRequestHandler):

    title = _('View Category')

    @has_permission('admin')
    def get(self, ID):

        C = self.db.query(CMSCategory).get(ID)
        if not C:
            return self.write( _('Can not find category %s' % ID) )

        C.children = self.db.query(CMSCategory).filter_by(
            parent_id = C.id ).all()

        d = { 'category': C }

        self.render('admin/cms/category/view.html', **d)


class CategoryRequestHandler(RequestHandler):

    @has_permission('admin')
    def prepare(self):

        self.category_list = [('0', None)]
        for C in self.db.query(CMSCategory).all():
            self.category_list.append( (str(C.id), C.name) )


class AddCategory(CategoryRequestHandler):

    title = _('Add CMS Category')
    template_path = 'admin/cms/add_category.html'

    def get(self):
        form = CategoryForm(self)
        form.parent.choices = self.category_list
        form.process()

        self.render(form = form)

    def post(self):

        form = CategoryForm(self)
        form.parent.choices = self.category_list

        d = { 'form': form }
        if form.validate():
            C = CMSCategory( name        = form.name.data,
                             summary     = form.summary.data,
                             description = form.description.data )
            PID = self.get_int( form.parent.data )
            P = self.db.query(CMSCategory).get( PID )
            if P:
                C.parent_id = P.id
            self.db.add(C)
            self.db.commit()
            url = self.reverse_url('admin:cms:category')
            return self.redirect( url )

        self.render(**d)


class EditCategory(CategoryRequestHandler):

    title = _('Edit CMS Category')
    template_path = 'admin/cms/edit_category.html'

    def get_category_list(self, ID):
        if isinstance(ID, int):
            ID = str(ID)

        new_list = []
        for k, v in self.category_list:
            if ID != k:
                new_list.append( (k, v) )

        return new_list


    def get(self, ID):

        C = self.db.query(CMSCategory).get(ID)
        if not C:
            return self.write( _('Can not find category %s.' % ID) )

        form = CategoryForm(self)
        form.parent.choices = self.get_category_list(ID)
        form.process()

        form.parent.default = C.parent_id
        form.name.data = C.name
        form.summary.data = C.summary
        form.description.data = C.description

        self.render(form = form)

    def post(self, ID):

        C = self.db.query(CMSCategory).get(ID)
        if not C:
            return self.write( _('Can not find category %s.' % ID) )

        form = CategoryForm(self)
        form.parent.choices = self.get_category_list(ID)

        d = { 'form': form }
        if form.validate():
            C.name        = form.name.data
            C.summary     = form.summary.data
            C.description = form.description.data

            ID = self.get_int( form.parent.data )
            P = self.db.query(CMSCategory).get( ID )
            if P:
                C.parent_id = P.id

            self.db.add(C)
            self.db.commit()

            url =  self.reverse_url('admin:cms:category')
            return self.redirect( url )

        self.render(**d)


class ajaxDeleteCategory(RequestHandler):

    @has_permission('admin')
    def post(self):

        success_ids, failed_ids = [], []

        IDS = self.get_argument('ids', [])
        IDS = json.loads(IDS)

        for x in IDS:
            E = self.db.query(CMSCategory).get(x)
            if E:
                self.db.delete(E)
                success_ids.append(E.id)
            else:
                failed_ids.append(x)

        self.db.commit()

        data = { 'return_code': 0,
                 'success_ids': success_ids,
                 'failed_ids': failed_ids }

        self.write(data)


class ArticleRequestHandler(RequestHandler):

    @has_permission('admin')
    def prepare(self):

        self.category_list = []
        for C in self.db.query(CMSCategory).all():
            self.category_list.append( (str(C.id), C.name) )


class AddArticle(ArticleRequestHandler):

    title = _('New Article')
    template_path = 'admin/cms/article/add.html'

    def get(self):

        form = ArticleForm(self)
        form.category.choices = self.category_list
        form.process()

        ID = self.get_argument_int('category')
        C = self.db.query(CMSCategory).get( ID )
        if C:
            form.category.default = C.id

        self.render(form = form)

    def post(self):

        form = ArticleForm(self)
        form.category.choices = self.category_list

        d = { 'form': form }
        if form.validate():
            A = CMSArticle( name    = form.name.data,
                            summary = form.summary.data,
                            body    = form.body.data )
            A.user = self.current_user
            ID = self.get_int( form.category.data )
            C = self.db.query(CMSCategory).get( ID )
            if C:
                A.category_id = C.id
                url = self.reverse_url('admin:cms:category:view', ID)
            else:
                url = self.reverse_url('admin:cms')

            self.db.add(A)
            self.db.commit()

            return self.redirect( url )

        self.render(**d)



class EditArticle(ArticleRequestHandler):

    title = _('New Article')
    template_path = 'admin/cms/article/edit.html'

    def get(self, ID):

        A = self.db.query(CMSArticle).get(ID)
        if not A:
            return self.write( _("Can not find article %s" % ID) )

        form = ArticleForm(self)
        form.category.choices = self.category_list
        form.process()

        form.category.default = A.category_id
        form.name.data        = A.name
        form.summary.data     = A.summary
        form.body.data        = A.body

        self.render(form = form)

    def post(self, ID):

        A = self.db.query(CMSArticle).get(ID)
        if not A:
            return self.write( _("Can not find article %s" % ID) )

        form = ArticleForm(self)
        form.category.choices = self.category_list

        d = { 'form': form }
        if form.validate():
            A.name    = form.name.data
            A.summary = form.summary.data
            A.body    = form.body.data
            A.user    = self.current_user

            ID = self.get_int( form.category.data )
            C = self.db.query(CMSCategory).get( ID )
            if C:
                A.category_id = C.id
                url = self.reverse_url('admin:cms:category:view', ID)
            else:
                url = self.reverse_url('admin:cms')

            self.db.add(A)
            self.db.commit()

            return self.redirect( url )

        self.render(**d)
