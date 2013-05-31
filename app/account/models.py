#/usr/bin/env python2.5

import os, random, json, datetime
from hashlib import sha1

from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref


class ResetPasswordApply(ORMBase):
    '''reset password apply'''

    __tablename__ = 'reset_password_apply'

    id = Column(Integer, primary_key=True)
    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User", order_by = id)
    key = Column( String(128) )
    created  = Column( DateTime(), default=datetime.datetime.now )

    def __init__(self, user):
        self.key = sha1(str(random.random())).hexdigest()
        self.user_id = user.id

    def __repr__(self):
        return '<ResetPasswordApply (%(user_id)s:%(username)s)>' % (
            self.user_id, self.user.username)
