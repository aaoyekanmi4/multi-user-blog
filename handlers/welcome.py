import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class WelcomeHandler(Handler):

    def get(self):
        username = self.get_user()
        if username:
            self.render("welcome.html", username = username)
        else:
            self.redirect('/signup')