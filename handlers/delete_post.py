import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler


class DeletePost(Handler):

    def get(self, post_id):
        self.this_user = self.get_user()
        self.p = BlogInfo.get_by_id(int(post_id))
        if self.this_user:
            if self.p and self.this_user == self.p.author:
                self.title = self.p.title
                self.p.delete()
                self.render("deleted.html", title = self.title)
            else:
                self.redirect('/blog')
        else:
            self.redirect('/login')
