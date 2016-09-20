import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class NewPost(Handler):

    def get (self):

        self.this_user = self.get_user()
        params = dict(this_user = self.this_user)
        if self.this_user:
            params.update(main.loggedin_params)
            self.render("new_post.html", **params)

        else:
            self.redirect('/login')

    def post(self):
        self.title = self.request.get("title")
        self.content = self.request.get("content")
        self.author = self.get_user()

        params = dict(title = self.title, content=self.content,
                      this_user = self.author)

        if self.author and self.title and self.content:

                blogpost = BlogInfo(content = self.content,
                                    title = self.title,
                                    author = self.author)
                blogpost.put()

                likes_value = 0
                dislikes_value = 0
                who_rated = []
                associated_post = blogpost.key().id()
                like_status = Likes(likes_value = likes_value,
                                    dislikes_value = dislikes_value,
                                    associated_post = associated_post,
                                    who_rated = who_rated,
                                    parent = blogpost)
                like_status.put()

                self.redirect("/blog/%s" % str(blogpost.key().id()))

        elif self.author and not (self.title and self.content):
            params.update(main.loggedin_params)
            params["error"] = "Please provide the content and the title"
            self.render("new_post.html", **params)
        else:
            params.update(main.loggedout_params)
            params["error"] = "Please log in to make a post"
            self.render("new_post.html", **params)