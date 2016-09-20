import jinja2
import webapp2
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from mainhandler import Handler
import main


class SignUp(Handler):

    def create_user(self, username, password):
        hashed_value = main.make_pw_hash(username, password)
        new_user = User(username = username, hashed_value = hashed_value)
        new_user.put()
        _id = str(new_user.key().id())
        user_id_val = main.make_secure_val(_id)
        self.response.headers.add_header('Set-Cookie',
                                         'user_id = %s; Path=/'
                                         % user_id_val)

    def get(self):
        self.render("sign_up.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.this_user = User.all().filter('username =', self.username).get()

        params = dict(username = self.username,
                      email = self.email)

        if self.this_user:
            params['username_used'] = "That user name is already taken"
            have_error = True

        if not main.valid_name(self.username):
            params['username_error'] = "That's not a valid username."
            have_error = True

        if not main.valid_password(self.password):
            params['password_error'] = "That wasn't a valid password."
            have_error = True

        elif self.password != self.verify:
            params['verify_error'] = "Your passwords didn't match."
            have_error = True

        if self.email and not main.valid_email(self.email):
            params['email_error'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('sign_up.html', **params)
        else:
            self.create_user(self.username, self.password)
            self.redirect('/welcome')