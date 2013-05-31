from tornado.web import url
from . import views

handlers = [

    ( r'/login', views.Login ),
    ( r'/logout', views.Logout ),

]
