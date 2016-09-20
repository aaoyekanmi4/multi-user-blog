import jinja2
import os
import webapp2
import re
from google.appengine.ext import db
from models import BlogInfo, Likes, User, Comment
from handlers import Handler, LoginHandler, SignUp, WelcomeHandler, NewPost
from handlers import MainPage, Permalink, EditComment, EditPost, DeletePost
from handlers import DeleteComment, RatePost, Logout
import string
import hashlib
import random
import hmac
import text


# Get templates from folder

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


# Check for valid username, password, and email with regular expressions

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_name(username):
    return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASSWORD_RE.match(password)


EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)


# Functions for hashing and checking username

def hash_str(s):
    return hmac.new(text.secret, s).hexdigest()

def make_secure_val (s):
    return "%s|%s" %(s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


# Functions for hashing and checking passwords

def make_salt():
    return ''.join(random.choice(string.letters) for x in range (5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (salt, h)

def valid_pw(name, pw, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, pw, salt)

# Links for user when logged-out

logout_ = "logout"
logged_in_as_ = "logged in as"
create_ = "Create new post"
edit_ = "Edit"

loggedin_params = dict(logout = logout_, logged_in_as = logged_in_as_,
                       create = create_, edit = edit_)

# Links for user when logged-in

signup_ = "sign-up |"
login_ = "login"

loggedout_params = dict(signup = signup_, login = login_)



app = webapp2.WSGIApplication([('/signup', SignUp),
                            ('/welcome', WelcomeHandler),
                            ('/login', LoginHandler),
                            ('/blog/newpost', NewPost),
                            ('/blog', MainPage),
                            ('/', MainPage),
                            ('/blog/([0-9]+)', Permalink),
                            ('/logout', Logout),
                            ('/blog/([0-9]+)/edit', EditPost),
                            ('/editcomments/([0-9]+)/([0-9]+)', EditComment),
                            ('/delcomment/([0-9]+)/([0-9]+)', DeleteComment),
                            ('/delpost/([0-9]+)', DeletePost),
                            ('/rate/([0-9]+)/([0-9]+)', RatePost)],
                             debug = True)








