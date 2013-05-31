from tornado.web import url
from . import views

handlers = [
#    url( r'/register', views.RegisterApply, name='register'),
    url( r'/register', views.Register, name='register'),
]
