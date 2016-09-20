import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class LoginHandler(Handler):

    def get(self):
        self.render("login.html")

    def post(self):
        have_error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.this_user = User.all().filter('username =', self.username).get()


        params =  dict(username = self.username,
                       password = self.password,
                       this_user = self.this_user)


        username_not_found = "No user by that name"
        invalid_login = "Invalid Login"
        wrong_password = "Password incorrect"

        if not self.this_user:
            params['username_not_found'] = "No user by that name"
            have_error = True

        elif not main.valid_pw(self.username, self.password,
                          self.this_user.hashed_value):
            params['wrong_password'] = "Password incorrect"
            have_error = True

        if not main.valid_name(self.username) or not main.valid_password(self.password):
            params['invalid_login'] = "Invalid Login"
            have_error = True

        if have_error:
            self.render("login.html", **params)

        else:
            _id = str(self.this_user.key().id())
            user_id_val = main.make_secure_val(_id)
            self.response.headers.add_header('Set-Cookie',
                'user_id = %s; Path=/' % user_id_val)
            self.redirect('/blog')