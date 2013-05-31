#/usr/bin/env python2.5

import os, random, json, datetime
from hashlib import sha1

from yweb.orm import db, ORMBase

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref



user_groups = Table('user_groups', ORMBase.metadata,
    Column('id', Integer, Sequence('user_groups_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey('auth_user.id')),
    Column('group_id', Integer, ForeignKey('auth_group.id'))
)


group_permissions = Table('group_permissions', ORMBase.metadata,
    Column('id', Integer, Sequence('group_permissions_id_seq'), primary_key=True),
    Column('group_id', Integer, ForeignKey('auth_group.id')),
    Column('permission_id', Integer, ForeignKey('auth_permission.id')),
)


class Group(ORMBase):

    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column( String(30) )
    description = Column( Text() )

    #TODO: a flag, can not delete when the flag is set !!!
    islocked = Column( Boolean, default = False)


    def __init__(self, name, description = None, islocked = False):
        self.name = name
        self.islocked = islocked
        if description:
            self.description = description


    def __repr__(self):
        return _("[Group(%s)]") % self.name


_default_locale = "en_US"

class User(ORMBase):

    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    username   = Column( String(30) )
    password   = Column( String(142) )
    email      = Column( String(64) )

    first_name = Column( String(30) )
    last_name  = Column( String(30) )
    nickname   = Column( String(30) )
    gender     = Column( Boolean )

    is_staff     = Column( Boolean, default = False )
    is_active    = Column( Boolean, default = True )
    is_superuser = Column( Boolean, default = False )
    is_locked    = Column( Boolean, default = False )

    locale = Column( String(12), default=_default_locale ) # user's language

    last_login  = Column( DateTime(), default=datetime.datetime.now )
    date_joined = Column( DateTime(), default=datetime.datetime.now )

    groups = relationship( 'Group', secondary=user_groups, backref='users' )

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __unicode__(self):
        return '<user(%s)>' % self.username

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save()
        return check_password(raw_password, self.password, setter)



class Permission(ORMBase):

    __tablename__ = 'auth_permission'

    id = Column(Integer, primary_key=True)
    name = Column( String(80) )
    codename = Column( String(100) )

    groups = relationship( "Group", secondary=group_permissions,
                           backref="permissions" )


    def __init__(self, name, codename):
        self.name = name
        self.codename = codename

    def __repr__(self):
        return _("[UserPermission(%s)]") % self.name

