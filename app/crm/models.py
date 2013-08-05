import datetime
from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref

from markdown import Markdown
YMK = Markdown(extensions=['fenced_code', 'tables'])



crm_contact_detail__customer = Table('crm_contact_detail__customer', ORMBase.metadata,
    Column('id', Integer, Sequence('crm_contact_detail__customer_id_seq'), primary_key=True),
    Column('detail_id', Integer, ForeignKey('crm_contact_detail.id')),
    Column('customer_id', Integer, ForeignKey('crm_customer.id')),
)


crm_contact_detail__contact = Table('crm_contact_detail__contact', ORMBase.metadata,
    Column('id', Integer, Sequence('crm_contact_detail__contact_id_seq'), primary_key=True),
    Column('detail_id', Integer, ForeignKey('crm_contact_detail.id')),
    Column('contact_id', Integer, ForeignKey('crm_contact.id'))
)



class CRMCustomer(ORMBase):

    __tablename__ = 'crm_customer'

    id = Column(Integer, Sequence('crm_customer_id_seq'), primary_key=True)

    name = Column(String(256))
    description = Column(Text, default='')

    user_id = Column(Integer, ForeignKey('auth_user.id'))
    user = relationship('User', order_by = id)

    details = relationship( 'CRMContactDetail',
                            secondary=crm_contact_detail__customer,
                            backref='customers' )

    created = Column(DateTime(), default=datetime.datetime.now)
    updated = Column(DateTime(), default=datetime.datetime.now)


    @property
    def description_html(self):
        return YMK.convert( self.description )


class CRMContact(ORMBase):

    __tablename__ = 'crm_contact'

    id = Column(Integer, Sequence('crm_contact_id_seq'), primary_key=True)

    customer_id = Column(Integer, ForeignKey('crm_customer.id'))
    customer = relationship('CRMCustomer', backref=backref('contacts'))

    name = Column(String(128))
    nickname = Column(String(128))

    description = Column(Text, default='')

    user_id = Column(Integer, ForeignKey('auth_user.id'))
    user = relationship('User', order_by = id)

    details = relationship( 'CRMContactDetail',
                            secondary=crm_contact_detail__contact,
                            backref='contacts' )

    created = Column(DateTime(), default=datetime.datetime.now)
    updated = Column(DateTime(), default=datetime.datetime.now)

    @property
    def description_html(self):
        return YMK.convert( self.description )



contact_type = [
    (1, 'Mobile Phone'),
    (2, 'Telephone'),
    (3, 'Email'),
    (4, 'QQ'),
    (5, 'Skype'),
    (6, 'Address'),
    (7, 'Website'),
]


class CRMContactDetail(ORMBase):

    __tablename__ = 'crm_contact_detail'

    id = Column(Integer, Sequence('crm_contact_detail_id_seq'), primary_key=True)

    type = Column(Integer)
    data = Column(String(64))
    desc = Column(String(128))
    hit = Column(Integer, default=1)

    created = Column(DateTime(), default=datetime.datetime.now)
    updated = Column(DateTime(), default=datetime.datetime.now)

    @property
    def type_str(self):
        for k, v in contact_type:
            if k == self.type:
                return v

        return _('Unknown')

    @classmethod
    def type_choices(self):
        choices = []
        for k, v in contact_type:
            choices.append( (str(k), v) )
        return choices



interaction_type = [
    (1, 'Telephone'),
    (2, 'Visit'),
    (3, 'Email'),
    (4, 'QQ'),
    (5, 'Skype'),
    (100, 'Other'),
]


class CRMContactInteraction(ORMBase):

    __tablename__ = 'crm_contact_interaction'

    id = Column(Integer, Sequence('crm_contact_interaction_id_seq'), primary_key=True)

    type = Column(Integer)

    contact_id = Column(Integer, ForeignKey('crm_contact.id'))
    contact = relationship('CRMContact', backref=backref('interactions'))

    summary = Column(String(512))
    description = Column(Text, default='')

    user_id = Column(Integer, ForeignKey('auth_user.id'))
    user = relationship('User', order_by = id)

    started = Column(DateTime(), default=datetime.datetime.now)
    ended = Column(DateTime(), default=datetime.datetime.now)

    created = Column(DateTime(), default=datetime.datetime.now)
    updated = Column(DateTime(), default=datetime.datetime.now)


    @property
    def type_str(self):
        for k, v in interaction_type:
            if k == self.type:
                return v

        return _('Unknown')

    @classmethod
    def type_choices(self):
        choices = []
        for k, v in interaction_type:
            choices.append( (str(k), v) )
        return choices

    @property
    def description_html(self):
        return YMK.convert( self.description )

