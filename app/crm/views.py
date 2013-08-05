# coding: utf-8

import os

from tornado.web import authenticated
from sqlalchemy.sql.expression import asc, desc, func
from sqlalchemy import and_

from yweb.handler import RequestHandler, has_permission
from yweb.utils.pagination import pagination

from ..auth.models import User
from .models import CRMCustomer, CRMContact, CRMContactInteraction,\
    CRMContactDetail
from .forms import CRMCustomerForm, CRMCustomerAddForm, \
    CRMContactAddForm, CRMContactForm, CRMContactDetailAddForm, \
    CRMContactInteractionForm


class Index(RequestHandler):

    @has_permission('admin')
    def get(self):

        customer_list = self.db.query(CRMCustomer).all()
        contact_list = self.db.query(CRMContact).all()
        interaction_list = self.db.query(CRMContactInteraction).all()

        d = { 'title': _('CRM Home'),
              'customer_list': customer_list,
              'contact_list': contact_list,
              'interaction_list': interaction_list }

        self.render('crm/index.html', **d)



class CustomerIndex(RequestHandler):

    @has_permission('admin')
    def get(self):

        customer_list = self.db.query(CRMCustomer).all()

        d = { 'title': _('CRM Customer List'),
              'customer_list': customer_list }

        self.render('crm/customer/index.html', **d)



class CustomerView(RequestHandler):

    @has_permission('admin')
    def get(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.write( _('Give me customer id please.') )

        C = self.db.query(CRMCustomer).get( ID )
        if not C:
            return self.write( _('Can not find customer %s') % ID )

        d = { 'title': _('View customer: %s') % C.name,
              'customer': C }

        self.render('crm/customer/view.html', **d)



class CustomerAdd(RequestHandler):

    title = _('Add a customer')
    template_path = 'crm/customer/add.html'

    @has_permission('admin')
    def prepare(self):

        form = CRMCustomerAddForm(self)
        self.prepare_kwargs['form'] = form

    def get(self):
        self.render()

    def post(self):

        form = self.prepare_kwargs['form']

        if form.validate():
            c = CRMCustomer( name = form.name.data,
                             description = form.description.data )

            c.user_id = self.current_user.id

            self.db.add(c)
            self.db.commit()

            url = self.reverse_url('crm:customer:view')
            url += '?id=%s' % c.id
            return self.redirect(url)

        self.render()

        

class CustomerEdit(RequestHandler):

    title = _('Edit customer')
    template_path = 'crm/customer/edit.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.finish( _('Give me customer id please.') )

        C = self.db.query(CRMCustomer).get( ID )
        if not C:
            return self.finish( _('Can not find customer %s') % ID )

        if C.user_id != self.current_user.id:
            return self.finish( _('Just owner can do it.') )

        form = CRMCustomerForm(self)
        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['customer'] = C

    def get(self):
        form = self.prepare_kwargs['form']
        C = self.prepare_kwargs['customer']

        form.name.data = C.name
        form.description.data = C.description

        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        C = self.prepare_kwargs['customer']

        if form.validate():
            C.name = form.name.data
            C.description = form.description.data

            self.db.commit()

            url = self.reverse_url('crm:customer:view')
            url += '?id=%s' % C.id
            return self.redirect(url)

        self.render()



class CustomerContactDetailAdd(RequestHandler):

    title = _('Add a contact detail for customer')
    template_path = 'crm/customer/detail_add.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('customer_id', None)
        if not ID:
            return self.finish( _('Give me customer id please.') )

        C = self.db.query(CRMCustomer).get( ID )
        if not C:
            return self.finish( _('Can not find customer %s') % ID )

        form = CRMContactDetailAddForm(self)
        form.type.choices = CRMContactDetail.type_choices()

        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['customer'] = C

    def get(self):
        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        customer = self.prepare_kwargs['customer']

        if form.validate():

            old = self.db.query(CRMContactDetail).filter(
                and_( CRMContactDetail.type == form.type.data,
                      CRMContactDetail.data == form.data.data )
                ).first()

            if old:
                if old not in customer.details:
                    customer.details.append( old )
                    old.hit += 1
                else:
                    # exists
                    pass
            else:
                d = CRMContactDetail( type = form.type.data,
                                      data = form.data.data,
                                      desc = form.desc.data )
                customer.details.append( d )
                self.db.add(d)

            self.db.commit()

            url = self.reverse_url('crm:customer:view')
            url += '?id=%s' % customer.id

            return self.redirect(url)

        self.render()



class ContactIndex(RequestHandler):

    @has_permission('admin')
    def get(self):

        contact_list = self.db.query(CRMContact).all()

        d = { 'title': _('CRM Contact List'),
              'contact_list': contact_list }

        self.render('crm/contact/index.html', **d)



class ContactView(RequestHandler):

    @has_permission('admin')
    def get(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.write( _('Give me contact id please.') )

        C = self.db.query(CRMContact).get( ID )
        if not C:
            return self.write( _('Can not find contact %s') % ID )

        d = { 'title': _('View contact: %s') % C.name,
              'contact': C }

        self.render('crm/contact/view.html', **d)




class ContactAdd(RequestHandler):

    title = _('Add a contact')
    template_path = 'crm/contact/add.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('customer_id', None)
        if not ID:
            return self.finish( _('Give me customer id please.') )

        C = self.db.query(CRMCustomer).get( ID )
        if not C:
            return self.finish( _('Can not find customer %s') % ID )

        form = CRMContactAddForm(self)
        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['customer'] = C

    def get(self):
        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        customer = self.prepare_kwargs['customer']

        if form.validate():

            old = self.db.query(CRMContact).filter(
                and_( CRMContact.name == form.name.data,
                      CRMContact.customer_id == customer.id )
                ).first()

            if old:
                form.name.errors.append( _('This contact is exist.') )
            else:

                c = CRMContact( name = form.name.data,
                                nickname = form.nickname.data,
                                description = form.description.data )
                c.customer_id = customer.id
                c.user_id = self.current_user.id

                self.db.add(c)
                self.db.commit()

                url = self.reverse_url('crm:contact:view')
                url += '?id=%s' % c.id
                return self.redirect(url)

        self.render()



class ContactEdit(RequestHandler):

    title = _('Edit contact')
    template_path = 'crm/contact/edit.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.finish( _('Give me contact id please.') )

        C = self.db.query(CRMContact).get( ID )
        if not C:
            return self.finish( _('Can not find contact %s') % ID )

        if C.user_id != self.current_user.id:
            return self.finish( _('Just owner can do it.') )

        form = CRMContactForm(self)
        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['contact'] = C

    def get(self):

        form = self.prepare_kwargs['form']
        contact = self.prepare_kwargs['contact']

        form.name.data = contact.name
        form.nickname.data = contact.nickname
        form.description.data = contact.description

        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        contact = self.prepare_kwargs['contact']

        if form.validate():

            contact.name = form.name.data
            contact.nickname = form.nickname.data
            contact.description = form.description.data

            self.db.commit()

            url = self.reverse_url('crm:contact:view')
            url += '?id=%s' % contact.id
            return self.redirect(url)

        self.render()



class ContactDetailAdd(RequestHandler):

    title = _('Add a contact detail')
    template_path = 'crm/contact/detail_add.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('contact_id', None)
        if not ID:
            return self.finish( _('Give me contact id please.') )

        C = self.db.query(CRMContact).get( ID )
        if not C:
            return self.finish( _('Can not find contact %s') % ID )

        form = CRMContactDetailAddForm(self)
        form.type.choices = CRMContactDetail.type_choices()

        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['contact'] = C

    def get(self):
        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        contact = self.prepare_kwargs['contact']

        if form.validate():

            old = self.db.query(CRMContactDetail).filter(
                and_( CRMContactDetail.type == form.type.data,
                      CRMContactDetail.data == form.data.data )
                ).first()

            if old:
                if old not in contact.details:
                    contact.details.append( old )
                    old.hit += 1
                else:
                    # exists
                    pass
            else:
                d = CRMContactDetail( type = form.type.data,
                                      data = form.data.data,
                                      desc = form.desc.data )

                contact.details.append( d )
                self.db.add(d)

            self.db.commit()

            url = self.reverse_url('crm:contact:view')
            url += '?id=%s' % contact.id

            return self.redirect(url)

        self.render()



class ContactDetailDelete(RequestHandler):

    @has_permission('admin')
    def get(self):

        detail_id = self.get_argument_int('id', None)
        if not detail_id:
            return self.write( _('Give me contact detail id please.') )

        detail = self.db.query(CRMContactDetail).get( detail_id )
        if not detail:
            return self.write( _('Can not find contact detail %s') % detail_id )

        contact_id = self.get_argument_int('contact_id', None)
        if not contact_id:
            return self.write( _('Give me contact id please.') )

        contact = self.db.query(CRMContact).get( contact_id )
        if not contact:
            return self.write( _('Can not find contact %s') % contact_id )

        contact.details.remove( detail )
        detail.hit -= 1
        if detail.hit <= 0:
            self.db.delete(detail)
        self.db.commit()

        url = self.reverse_url('crm:contact:view')
        url += '?id=%s' % contact.id

        self.redirect( url )



class ContactInteractionView(RequestHandler):

    @has_permission('admin')
    def get(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.finish( _('Give me interaction id please.') )

        I = self.db.query(CRMContactInteraction).get( ID )
        if not I:
            return self.finish( _('Can not find interaction %s') % ID )

        d = { 'title': _('View Interaction %s') % I.summary,
              'interaction': I }

        self.render('crm/contact/interaction_view.html', **d)



class ContactInteractionAdd(RequestHandler):

    title = _('Add a contact interaction')
    template_path = 'crm/contact/interaction_add.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('contact_id', None)
        if not ID:
            return self.finish( _('Give me contact id please.') )

        C = self.db.query(CRMContact).get( ID )
        if not C:
            return self.finish( _('Can not find contact %s') % ID )

        form = CRMContactInteractionForm(self)
        form.type.choices = CRMContactInteraction.type_choices()

        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['contact'] = C

    def get(self):
        self.render()

    def post(self):

        form = self.prepare_kwargs['form']
        contact = self.prepare_kwargs['contact']

        if form.validate():

            I = CRMContactInteraction(
                type        = form.type.data,
                summary     = form.summary.data,
                description = form.description.data,
                started     = form.started.data,
                ended       = form.ended.data )

            I.contact_id = contact.id
            I.user_id = self.current_user.id

            self.db.add(I)
            self.db.commit()

            url = self.reverse_url('crm:contact:view')
            url += '?id=%s' % contact.id

            return self.redirect(url)

        self.render()



class ContactInteractionEdit(RequestHandler):

    title = _('Edit contact interaction')
    template_path = 'crm/contact/interaction_edit.html'

    @has_permission('admin')
    def prepare(self):

        ID = self.get_argument_int('id', None)
        if not ID:
            return self.finish( _('Give me interaction id please.') )

        I = self.db.query(CRMContactInteraction).get( ID )
        if not I:
            return self.finish( _('Can not find interaction %s') % ID )

        if I.user_id != self.current_user.id:
            return self.finish( _('Just owner can do it.') )

        form = CRMContactInteractionForm(self)
        form.type.choices = CRMContactInteraction.type_choices()

        self.prepare_kwargs['form'] = form
        self.prepare_kwargs['interaction'] = I

    def get(self):

        form = self.prepare_kwargs['form']
        I = self.prepare_kwargs['interaction']

        form.type.default = I.type
        form.process()

        form.summary.data = I.summary
        form.description.data = I.description
        form.started.data = I.started
        form.ended.data = I.ended

        self.render()


    def post(self):

        form = self.prepare_kwargs['form']
        I = self.prepare_kwargs['interaction']

        if form.validate():

            I.type        = form.type.data
            I.summary     = form.summary.data
            I.description = form.description.data
            I.started     = form.started.data
            I.ended       = form.ended.data

            self.db.commit()

            url = self.reverse_url('crm:contact:interaction:view')
            url += '?id=%s' % I.id

            return self.redirect(url)

        self.render()

