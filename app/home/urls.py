from tornado.web import url
from . import views
from . import admin_views

handlers = [

    url( r'/', views.Index, name='home:index'),
    ( r'/no_permission', views.NoPermission ),
    ( r'/setlocale', views.SetLocale ),

    # admin handlers
    url( r'/admin', admin_views.Index, name='admin:index'),

]
