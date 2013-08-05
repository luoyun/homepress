from tornado.web import url
from . import views

handlers = [

    url( r'/crm', views.Index, name="crm"),

    # customer
    url( r'/crm/customer', views.CustomerIndex,
         name="crm:customer"),

    url( r'/crm/customer/view', views.CustomerView,
         name="crm:customer:view"),

    url( r'/crm/customer/add', views.CustomerAdd,
         name="crm:customer:add"),

    url( r'/crm/customer/edit', views.CustomerEdit,
         name="crm:customer:edit"),

    # customer contact detail
    url( r'/crm/customer/detail/add', views.CustomerContactDetailAdd,
         name="crm:customer:detail:add"),

    # contact
    url( r'/crm/contact', views.ContactIndex,
         name="crm:contact"),

    url( r'/crm/contact/add', views.ContactAdd,
         name="crm:contact:add"),

    url( r'/crm/contact/edit', views.ContactEdit,
         name="crm:contact:edit"),

    url( r'/crm/contact/view', views.ContactView,
         name="crm:contact:view"),

    # contact detail
    url( r'/crm/contact/detail/add', views.ContactDetailAdd,
         name="crm:contact:detail:add"),

    url( r'/crm/contact/detail/delete', views.ContactDetailDelete,
         name="crm:contact:detail:delete"),

    # contact interaction
    url( r'/crm/contact/interaction/add',
         views.ContactInteractionAdd,
         name="crm:contact:interaction:add"),

    url( r'/crm/contact/interaction/view',
         views.ContactInteractionView,
         name="crm:contact:interaction:view"),

    url( r'/crm/contact/interaction/edit',
         views.ContactInteractionEdit,
         name="crm:contact:interaction:edit"),

]
