# coding: utf-8

import os, sys, ConfigParser

siteroot = os.path.dirname(os.path.realpath(__file__))

site_localedir = os.path.join(siteroot, 'locale')

sys.path.insert(0, os.path.join(siteroot, 'lib'))

# site config
sitecfg = os.path.join(siteroot, 'site.cfg')
sitecfg_changed = False # set this flag when sitecfg changed

#DB_URI = 'sqlite:///lab/sqlite-test.db'
DB_URI = "postgresql+psycopg2://luoyun:luoyun@127.0.0.1/mysite"

STATIC_PATH = os.path.join(siteroot, "static")
TEMPLATE_PATH = os.path.join(siteroot, "template")
STATIC_URL = "/static/"

THEME = "default"
THEME_URL = "/static/themes/%s/" % THEME

I18N_PATH = os.path.join(siteroot, "locale")

LANGUAGES = {
    "en_US": u"English (US)",
    "zh_CN": u"\u4e2d\u6587(\u7b80\u4f53)",
    }


app = [ 'yweb.contrib.session',
        'app.auth',
        'app.registration',
        'app.language',
        'app.account',
        'app.home',
        'app.site',
        'app.cms',
        'app.crm', ]

default_permission = [
    # ( 'codename', 'name' )
    ('admin', 'Administrator'),
]

default_group = [
    # ( 'group name' )
    ('admin'),
]

default_user = [
    # ( 'username', 'password' )
    ('admin', 'admin'),
    ('Jian', 'ffffff'),
]

default_user_group = [
    # ( 'group', 'user' )
    ('admin', 'admin'),
    ('admin', 'Jian'),
]

default_group_permission = [
    # ( 'group', 'permission' )
    ('admin', 'admin'),
]

default_admin_user = 'admin'
