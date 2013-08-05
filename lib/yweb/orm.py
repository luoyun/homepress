#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base



DB_URI = settings.DB_URI

ORMBase = declarative_base()

from sqlalchemy.pool import NullPool
dbengine = create_engine(DB_URI, echo=False)

#print dbengine.execute('show transaction isolation level').scalar()

session_factory = sessionmaker(bind=dbengine)
Session = scoped_session(session_factory)

db = Session()


def create_session():

    dbengine = create_engine(DB_URI, echo=False)
    session_factory = sessionmaker(bind=dbengine)
    Session = scoped_session(session_factory)

    return Session

