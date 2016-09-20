import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main

class DeleteComment(Handler):

    def get(self, post_id, c_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.comm = Comment.get_by_id(int(c_id), parent=self.p)
        self.this_user = self.get_user()
        if self.this_user:
            if self.comm and self.comm.comment_author == self.this_user:
                self.comm.delete()
                self.redirect("/blog/%s" % post_id)
            else:
                self.redirect('/blog')
        else:
            self.redirect('/login')