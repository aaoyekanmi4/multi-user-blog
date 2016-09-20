from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    hashed_value = db.TextProperty(required = True)
    email = db.StringProperty
