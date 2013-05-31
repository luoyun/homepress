#!/usr/bin/env python
# coding: utf-8

import settings
import os,sys,logging

logging.basicConfig()
lylog = logging.getLogger("Manage")
lylog.setLevel(logging.DEBUG)

import random, time, pickle, base64
from hashlib import md5, sha512, sha1

from app.auth.utils import enc_login_passwd

# TODO: i18n is too ugly yet
import gettext
gettext.install( 'app', settings.I18N_PATH, unicode=False )


def syncdb():

    for m in settings.app:
        try:
            exec "from %s.models import *" % m
        except ImportError, e:
            pass

    from yweb.orm import db, ORMBase, dbengine
    ORMBase.metadata.create_all(dbengine)

    default_value(db)
#    default_value2(db)

def default_value2(db):

    from app.site.models import SiteNav

    for T, L, N in [
        [1, 61, '产品'],
        [1, 61, '解决方案'],
        [1, 61, '新闻'],
        [1, 61, '文档'],
        [1, 61, '下载'],
        [1, 14, 'Products'],
        [1, 14, 'Solutions'],
        [2, 14,  'News'],
        [1, 14, 'Docs'],
        [1, 14, 'Download'],
        ]:
        e = SiteNav( type        = T,
                     language_id = L,
                     name        = N )
        db.add(e)


    from app.site.models import SiteEntry

    for slug in ['contact', 'about', 'what-is-cloud']:
        E = SiteEntry(slug = slug)
        db.add(E)


    from app.cms.models import CMSCategory

    for name in [ u'中文', 'English' ]:
        C = CMSCategory(name = name)
        db.add(C)


    db.commit()
    

def default_value(db):

    from app.auth.models import Group, Permission, User
    from yweb.locale import LANGUAGES
    from app.language.models import Language

    # languages
    for L in LANGUAGES:
        lang = db.query(Language).filter_by(codename = L['codename']).first()
        if lang: continue
        lang = Language( name = L['name'],
                         name_en = L['name_en'],
                         codename = L['codename'] )
        db.add(lang)

    # Permission
    for codename, name in settings.default_permission:
        p = db.query(Permission).filter_by(codename = codename).first()
        if p: continue
        p = Permission(codename = codename, name = name)
        db.add(p)

    # Group
    for name in settings.default_group:
        g = db.query(Group).filter_by(name=name).first()
        if g: continue
        g = Group(name = name, islocked = True)
        db.add(g)

    # User
    for username, password in settings.default_user:
        u = db.query(User).filter_by(username=username).first()
        if u: continue
        enc_password = enc_login_passwd(password)
        u = User(username = username, password = enc_password)
        db.add(u)

    # User Group
    for groupname, username in settings.default_user_group:
        u = db.query(User).filter_by(username=username).first()
        g = db.query(Group).filter_by(name=groupname).first()
        if u and (g not in u.groups):
            u.groups.append(g)

    # Group Permission
    for groupname, codename in settings.default_group_permission:
        g = db.query(Group).filter_by(name=groupname).first()
        p = db.query(Permission).filter_by(codename=codename).first()
        if p not in g.permissions:
            g.permissions.append(p)

    db.commit()


def i18n():

    import subprocess
    #settings.PROJECT_ROOT
    #settings.I18N_PATH
    for language in os.listdir(settings.I18N_PATH):
        language_path = os.path.join(settings.I18N_PATH, language)
        if os.path.isdir(language_path):
            po_path = os.path.join(language_path, 'LC_MESSAGES')
            for po in os.listdir(po_path):
                name, suffix = po.split('.')
                if suffix == 'po':
                    po_file = os.path.join(po_path, po)
                    mo_file = os.path.join(po_path, "%s.mo" % name)
                    cmd = 'msgfmt %s -o %s' % (po_file, mo_file)
                    try:
                        r = subprocess.call(cmd.split())
                    except Exception, e:
                        lylog.error('exec msgfmt error, maybe gettext was not install : %s' % e)
                    if r == 0:
                        lylog.debug('build %s success' % mo_file)
                    else:
                        lylog.error('build %s failed' % mo_file)


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        if sys.argv[1] == '--i18n':
            i18n()
            sys.exit(0)

    syncdb()
    i18n()
