from google.appengine.ext import db


class BlogInfo(db.Model):

    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified  = db.DateProperty(auto_now = True)
    author = db.StringProperty(required = True)