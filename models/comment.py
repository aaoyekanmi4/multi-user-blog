from google.appengine.ext import db

class Comment(db.Model):
    comment_text = db.TextProperty(required = True)
    comment_time = db.DateTimeProperty(auto_now_add = True)
    comment_author = db.StringProperty(required = True)
    associated_post = db.IntegerProperty(required = True)