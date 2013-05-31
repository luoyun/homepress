import datetime
from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref

from markdown import Markdown
YMK = Markdown(extensions=['fenced_code', 'tables'])


class CMSCategory(ORMBase):

    ''' CMS Category '''

    __tablename__ = 'cms_category'

    id          = Column(Integer, Sequence('cms_category_id_seq'), primary_key=True)
    parent_id   = Column(Integer, ForeignKey('cms_category.id'))
#    parent      = relationship("CMSCategory", backref=backref('children'))
    position    = Column(Integer, default=0)
    name        = Column(String(64))
    summary     = Column(String(1024), default='')
    description = Column(Text, default='')

    created     = Column(DateTime(), default=datetime.datetime.now)
    updated     = Column(DateTime(), default=datetime.datetime.now)

    def __str__(self):
        return 'CMSCategory <%s>' % self.id


ARTICLE_STATUS = (
    (0, _('Normal')),
    (1, _('Deleted')),
)

class CMSArticle(ORMBase):

    __tablename__ = 'cms_article'

    id          = Column(Integer, Sequence('cms_article_id_seq'), primary_key=True)
    category_id = Column(Integer, ForeignKey('cms_category.id'))
    category    = relationship('CMSCategory', backref=backref('articles'))

    name    = Column(String(256))
    summary = Column(String(1024))
    body    = Column(Text)

    user_id = Column(Integer, ForeignKey('auth_user.id'))
    user    = relationship('User', order_by = id)

    # is_locked : can not edit by anyone except admin
    is_locked  = Column(Boolean, default = False)
    # is_closed : can not reply now
    is_closed  = Column(Boolean, default = False)
    # is_visible : can visible
    is_visible = Column(Boolean, default = True)

    like   = Column(Integer, default=0)
    unlike = Column(Integer, default=0)
    visit  = Column(Integer, default=0) # view times

    position = Column(Integer, default=0) # topic can sort by position
    status   = Column(Integer, default=0) # topic status

    public_date = Column(DateTime(), default=datetime.datetime.now)
    created     = Column(DateTime(), default=datetime.datetime.now)
    updated     = Column(DateTime(), default=datetime.datetime.now)

    def __str__(self):
        return 'CMSArticle <%s>' % self.id

    def set_status(self, status):
        if status == 'deleted':
            self.status = 1

    @property
    def body_html(self):
        return YMK.convert( self.body )



class CMSComment(ORMBase):

    __tablename__ = 'cms_comment'

    id = Column(Integer, Sequence('cms_comment_id_seq'), primary_key=True)
    article_id = Column(Integer, ForeignKey('cms_article.id'))
    article = relationship('CMSArticle', backref=backref('comments'))

    # parent post
    parent_id = Column(Integer, ForeignKey('cms_comment.id'))
#    parent    = relationship('CMSPost', backref=backref('children'))

    body = Column(Text)

    user_id = Column(Integer, ForeignKey('auth_user.id'))
    user = relationship('User', order_by = id)

    # is_locked : can not edit by anyone except admin
    is_locked  = Column(Boolean, default = False)
    # is_visible : can visible
    is_visible = Column(Boolean, default = True)

    like   = Column(Integer, default=0)
    unlike = Column(Integer, default=0)

    created = Column(DateTime(), default=datetime.datetime.now)
    updated = Column(DateTime(), default=datetime.datetime.now)

    def __str__(self):
        return 'CMSComment <%s>' % self.id

