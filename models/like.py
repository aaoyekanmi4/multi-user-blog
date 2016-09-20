from google.appengine.ext import db

class Likes(db.Model):
    associated_post = db.IntegerProperty(required = True)
    who_rated = db.StringListProperty(required= True)
    likes_value = db.IntegerProperty(required = True)
    dislikes_value = db.IntegerProperty(required = True)