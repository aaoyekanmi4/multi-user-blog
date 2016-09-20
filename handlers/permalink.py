import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


# Unique page for each post
class Permalink(Handler):

    def get(self, post_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.like_status = Likes.all().ancestor(self.p).get()
        self.this_user = self.get_user()

        params = dict(p = self.p,
                      post_comments = self.post_comments,
                      like_status = self.like_status,
                      this_user = self.this_user)
        if self.this_user:
            params.update(main.loggedin_params)
            self.render("permalink.html", **params)

        else:
            params.update(main.loggedout_params)
            self.render("permalink.html", **params)

        if not self.p:
            self.error(404)
            return

# Post function on permalink that is used to post comments

    def post(self, post_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.like_status = Likes.all().ancestor(self.p).get()
        self.comment_author = self.get_user()
        self.comment_text = self.request.get("comment")

        params = dict(p = self.p,
                      post_comments = self.post_comments,
                      like_status = self.like_status,
                      this_user = self.comment_author)

        if self.comment_text and self.comment_author:

            comment = Comment(comment_text = self.comment_text,
                              comment_author = self.comment_author,
                              associated_post = int(post_id),
                              like_status = self.like_status,
                              parent=self.p)
            comment.put()
            self.redirect("/blog/%s" % post_id)

        elif self.comment_author and not self.comment_text:
            params.update(main.loggedin_params)
            params["no_comment"] = "Please enter text"
            self.render("permalink.html", **params)


        else:
            params.update(main.loggedout_params)
            params["cant_comment"] = "Please log in to comment"
            self.render("permalink.html", **params)