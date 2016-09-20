import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class EditComment(Handler):

    def get(self, post_id, c_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.comm = Comment.get_by_id(int(c_id), parent=self.p)
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.this_user = self.get_user()

        params = dict (comment_to_edit = self.comm,
            this_user = self.this_user, post_comments = self.post_comments)

        if self.this_user:
            if self.comm and self.comm.comment_author == self.this_user:
                params.update(main.loggedin_params)
                self.render("editcomment.html", **params)
            else:
                self.redirect('/blog')
        else:
            self.redirect('/login')


    def post(self, post_id, c_id):

        self.comment_text = self.request.get("comment")
        self.p = BlogInfo.get_by_id(int(post_id))
        self.comm = Comment.get_by_id(int(c_id), parent=self.p)
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.this_user = self.get_user()

        params = dict(comment_to_edit = self.comm,
            this_user = self.this_user, post_comments = self.post_comments)

        if not self.this_user:
            self.redirect('/login')

        if self.this_user == self.comm.comment_author:

            if not self.comment_text:
                params.update(main.loggedin_params)
                params["error"] = "Need content to post comment."
                self.render("editcomment.html", **params)

            else:
                self.comm = Comment.get_by_id(int(c_id), parent= self.p)
                self.comm.comment_text = self.comment_text
                self.comm.put()

                self.redirect("/blog/%s" % self.comm.associated_post)
        else:
            params.update(main.loggedin_params)
            params["error"] = "You may only edit your own comments."
            self.render("editcomment.html", **params)

