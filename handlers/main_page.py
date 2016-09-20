import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class MainPage (Handler):

    def get(self):
        self.blogposts = BlogInfo.all().order('-created')
        self.this_user = self.get_user()

        params = dict(blogposts = self.blogposts, this_user = self.this_user)

        if self.this_user:

            params.update(main.loggedin_params)
            self.render("blog.html", **params)
        else:
            params.update(main.loggedout_params)
            self.render("blog.html", **params)