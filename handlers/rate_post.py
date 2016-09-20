import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main



# Controls likes and dislikes
class RatePost(Handler):
    def get(self, post_id, is_liked):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.this_user = self.get_user()
        self.like_status = Likes.all().ancestor(self.p).get()
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)


        params = dict(p = self.p,
                      this_user = self.this_user,
                       like_status = self.like_status,
                       post_comments = self.post_comments)

        if self.this_user in self.like_status.who_rated:
            params["like_error"] = "You've already rated this post"
            params.update(main.loggedin_params)
            self.render("rate_error.html", **params)

        elif self.this_user and self.p.author != self.this_user:

            is_liked = int(is_liked)
            if is_liked == 0:
                self.like_status.likes_value += 1
                self.like_status.who_rated += [self.this_user]

                self.like_status.put()


                self.redirect("/blog/%s" % post_id)
            else:
                self.like_status.dislikes_value += 1
                self.like_status.who_rated += [self.this_user]
                self.like_status.put()

                self.redirect("/blog/%s" % post_id)



        elif self.p.author == self.this_user:
            params["like_error"] = "Not allowed to like and dislike own posts"
            params.update(main.loggedin_params)
            self.render("rate_error.html", **params)

        else:
            params["cant_like"] = "Please login to like and dislike posts"
            params.update(main.loggedout_params)
            self.render("rate_error.html", **params)