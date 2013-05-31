from tornado.web import url
from . import views
from . import admin_views

handlers = [

    url( r'/cms/category/([0-9]+)',
         views.ViewCategory, name="cms:category:view"),

    url( r'/cms/article/([0-9]+)',
         views.ViewArticle, name="cms:article:view"),

    # admin
    url( r'/admin/cms', admin_views.Index, name="admin:cms"),

    url( r'/admin/cms/category',
         admin_views.CategoryIndex, name="admin:cms:category"),

    url( r'/admin/cms/category/add',
         admin_views.AddCategory, name="admin:cms:add_category"),

    ( r'/admin/cms/category/delete', admin_views.ajaxDeleteCategory),

    url( r'/admin/cms/category/([0-9]+)',
         admin_views.ViewCategory, name="admin:cms:category:view"),

    url( r'/admin/cms/category/([0-9]+)/edit',
         admin_views.EditCategory, name="admin:cms:edit_category"),

    url( r'/admin/cms/article/add',
         admin_views.AddArticle, name="admin:cms:article:add"),

    url( r'/admin/cms/article/([0-9]+)/edit',
         admin_views.EditArticle, name="admin:cms:article:edit"),
]
#_handlers = [
#    url( r'/cms', views.Index, name="cms" ),
#
#    url( r'/cms/c/([0-9]+)', views.CatalogIndex,
#         name="cms:catalog" ),
#
#    url( r'/cms/t/add', views.TopicAdd,
#         name="cms:topic:add" ),
#
#    url( r'/cms/t/([0-9]+)', views.TopicView,
#         name="cms:topic" ),
#
#    url( r'/cms/t/([0-9]+)/edit', views.TopicEdit,
#         name="cms:topic:edit" ),
#
#    url( r'/cms/t/([0-9]+)/delete', views.TopicDelete,
#         name="cms:topic:delete" ),
#
#    url( r'/cms/t/([0-9]+)/like', views.TopicView,
#         name="cms:topic:like" ),
#
#    url( r'/cms/t/([0-9]+)/unlike', views.TopicView,
#         name="cms:topic:unlike" ),
#
#    url( r'/cms/t/([0-9]+)/reply', views.TopicReply,
#         name="cms:topic:reply" ),
#
#]
#
