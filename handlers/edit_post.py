import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class EditPost(Handler):

    def get(self, post_id):

        self.this_user = self.get_user()
        self.p = BlogInfo.get_by_id(int(post_id))

        params = dict(this_user = self.this_user,
                  p = self.p)

        if self.this_user:

            if self.p and self.this_user == self.p.author:
                params.update(main.loggedin_params)
                self.render("edit.html", **params)

            else:
                self.redirect('/blog')
        else:
            self.redirect('/login')


    def post(self, post_id):

        self.title = self.request.get("title")
        self.content = self.request.get("content")
        self.p = BlogInfo.get_by_id(int(post_id))

        params = dict(title = self.title, content = self.content,
                      p = self.p)

        if self.this_user == self.p.author:

            if self.title and self.content:
                self.p.title = self.title
                self.p.content = self.content
                self.p.put()
                self.redirect("/blog/%s" % post_id)

            else:
                params.update(main.loggedin_params)
                params["error"] = "Please provide the content and the title"
                self.render("edit.html", **params)
        else:
            params.update(main.loggedin_params)
            params["error"] = "You may only edit your own posts"
            self.render("edit.html", **params)

