#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

ORMBase = declarative_base()

dbengine = create_engine(settings.DB_URI, echo=False)

Session = sessionmaker(bind=dbengine)
db = Session()

