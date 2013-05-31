from tornado.web import url
from . import views

handlers = [
    url( r'/account', views.Index, name='account:index' ),
    url( r'/account/reset_password', views.ResetPassword,
         name='account:reset_password' ),
]
