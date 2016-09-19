import jinja2
import os
import webapp2
import re
from google.appengine.ext import db
import string
import hashlib
import random
import hmac
import text


#CODE FROM INTRO TO BACKEND CLASS
# Set up jinja to get templates from folder
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

# check for valid username, password, and email with regular expressions
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_name(username):
    return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASSWORD_RE.match(password)


EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)


# functions for hashing and checking username
def hash_str(s):
    return hmac.new(text.secret, s).hexdigest()

def make_secure_val (s):
    return "%s|%s" %(s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


# functions for hashing and checking passwords
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





# links for user when logged in or logged out
logout_ = "logout"
logged_in_as_ = "logged in as"
create_ = "Create new post"
edit_ = "Edit"

loggedin_params = dict(logout = logout_, logged_in_as = logged_in_as_,
                       create = create_, edit = edit_)


signup_ = "sign-up |"
login_ = "login"

loggedout_params = dict(signup = signup_, login = login_)


# create kinds (like sql tables)
class BlogInfo(db.Model):

    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified  = db.DateProperty(auto_now = True)
    author = db.StringProperty(required = True)



class Likes(db.Model):
    associated_post = db.IntegerProperty(required = True)
    who_rated = db.StringListProperty
    likes_value = db.IntegerProperty(required = True)
    dislikes_value = db.IntegerProperty(required = True)

class User(db.Model):
    username = db.StringProperty(required = True)
    hashed_value = db.TextProperty(required = True)
    email = db.StringProperty


class Comment(db.Model):
    comment_text = db.TextProperty(required = True)
    comment_time = db.DateTimeProperty(auto_now_add = True)
    comment_author = db.StringProperty(required = True)
    associated_post = db.IntegerProperty(required = True)

# functions for jinja2 to display template html files
class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_user(self):
        user_cookie_str =self.request.cookies.get("user_id")
        if user_cookie_str:
            cookie_val = check_secure_val(user_cookie_str)
            if cookie_val:
                this_user = User.get_by_id(int(cookie_val))
                return this_user.username

# handlers for each page


#signup code  from class

class SignUp(Handler):

    def create_user(self, username, password):
        hashed_value = make_pw_hash(username, password)
        new_user = User(username = username, hashed_value = hashed_value)
        new_user.put()
        _id = str(new_user.key().id())
        user_id_val = make_secure_val(_id)
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

        if not valid_name(self.username):
            params['username_error'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['password_error'] = "That wasn't a valid password."
            have_error = True

        elif self.password != self.verify:
            params['verify_error'] = "Your passwords didn't match."
            have_error = True

        if self.email and not valid_email(self.email):
            params['email_error'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('sign_up.html', **params)
        else:
            self.create_user(self.username, self.password)
            self.redirect('/welcome')



class WelcomeHandler(Handler):

    def get(self):
        username = self.get_user()
        if username:
            self.render("welcome.html", username = username)
        else:
            self.redirect('/signup')

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

        elif not valid_pw(self.username, self.password,
                          self.this_user.hashed_value):
            params['wrong_password'] = "Password incorrect"
            have_error = True

        if not valid_name(self.username) or not valid_password(self.password):
            params['invalid_login'] = "Invalid Login"
            have_error = True

        if have_error:
            self.render("login.html", **params)

        else:
            _id = str(self.this_user.key().id())
            user_id_val = make_secure_val(_id)
            self.response.headers.add_header('Set-Cookie',
                'user_id = %s; Path=/' % user_id_val)
            self.redirect('/blog')



class NewPost(Handler):

    def get (self):

        self.this_user = self.get_user()
        params = dict(this_user = self.this_user)
        if self.this_user:
            params.update(loggedin_params)
            self.render("new_post.html", **params)

        else:
            self.redirect('/blog')

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
            params.update(loggedin_params)
            params["error"] = "Please provide the content and the title"
            self.render("new_post.html", **params)
        else:
            params.update(loggedout_params)
            params["error"] = "Please log in to make a post"
            self.render("new_post.html", **params)


class MainPage (Handler):

    def get(self):
        self.blogposts = BlogInfo.all().order('-created')
        self.this_user = self.get_user()

        params = dict(blogposts = self.blogposts, this_user = self.this_user)

        if self.this_user:

            params.update(loggedin_params)
            self.render("blog.html", **params)
        else:
            params.update(loggedout_params)
            self.render("blog.html", **params)


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
            params.update(loggedin_params)
            self.render("permalink.html", **params)

        else:
            params.update(loggedout_params)
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
            params.update(loggedin_params)
            params["no_comment"] = "Please enter text"
            self.render("permalink.html", **params)


        else:
            params.update(loggedout_params)
            params["cant_comment"] = "Please log in to comment"
            self.render("permalink.html", **params)


class EditComment(Handler):

    def get(self, post_id, c_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.e_comment = Comment.get_by_id(int(c_id), parent=self.p)
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.this_user = self.get_user()

        params = dict (comment_to_edit = self.e_comment,
            this_user = self.this_user, post_comments = self.post_comments)

        if self.this_user == self.e_comment.comment_author:
            params.update(loggedin_params)
            self.render("editcomment.html", **params)

        else:
            self.redirect('/blog')


    def post(self, post_id, c_id):

        self.comment_text = self.request.get("comment")
        self.p = BlogInfo.get_by_id(int(post_id))
        self.e_comment = Comment.get_by_id(int(c_id), parent=self.p)
        self.post_comments = Comment.all().ancestor(self.p).fetch(limit=10)
        self.this_user = self.get_user()

        params = dict(comment_to_edit = self.e_comment,
            this_user = self.this_user, post_comments = self.post_comments)

        if not self.comment_text:
            params.update(loggedin_params)
            params["error"] = "Need content to post comment."
            self.render("editcomment.html", **params)

        else:
            self.e_comment = Comment.get_by_id(int(c_id), parent= self.p)
            self.e_comment.comment_text = self.comment_text
            self.e_comment.put()

            self.redirect("/blog/%s" % self.e_comment.associated_post)




class Editpost(Handler):

    def get(self, post_id):

        self.this_user = self.get_user()
        self.p = BlogInfo.get_by_id(int(post_id))

        params = dict(this_user = self.this_user,
                  p = self.p)


        if self.p and self.this_user == self.p.author:
            params.update(loggedin_params)
            self.render("edit.html", **params)

        else:
            self.error(404)
            return


    def post(self, post_id):

        self.title = self.request.get("title")
        self.content = self.request.get("content")
        self.p = BlogInfo.get_by_id(int(post_id))

        params = dict(title = self.title, content = self.content,
                      p = self.p)

        if self.title and self.content:
            self.p.title = self.title
            self.p.content = self.content
            self.p.put()
            self.redirect("/blog/%s" % post_id)

        else:
            params.update(loggedin_params)
            params["error"] = "Please provide the content and the title"
            self.render("edit.html", **params)



class DeletePost(Handler):

    def get(self, post_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        if self.p:
            self.title = self.p.title
            self.p.delete()

            self.render("deleted.html", title = self.title)
        else:
            self.error(404)
            return



class DeleteComment(Handler):

    def get(self, post_id, c_id):

        self.p = BlogInfo.get_by_id(int(post_id))
        self.comment_to_edit = Comment.get_by_id(int(c_id), parent=self.p)
        if self.comment_to_edit:
            self.comment_to_edit.delete()
            self.redirect("/blog/%s" % post_id)
        else:
            self.error(404)
            return



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


        if self.this_user and self.p.author != self.this_user:

            is_liked = int(is_liked)
            if is_liked == 0:
                self.like_status.likes_value += 1
                self.like_status.who_rated = self.this_user

                self.like_status.put()


                self.redirect("/blog/%s" % post_id)
            else:
                self.like_status.dislikes_value += 1
                self.like_status.who_rated = self.this_user
                self.like_status.put()

                self.redirect("/blog/%s" % post_id)



        elif self.p.author == self.this_user:
            params["like_error"] = "Not allowed to like and dislike own posts"
            params.update(loggedin_params)
            self.render("permalink.html", **params)

        else:
            params["cant_like"] = "Please login to like and dislike posts"
            params.update(loggedout_params)
            self.render("permalink.html", **params)





class Logout(Handler):

    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id =; Path=/')
        self.redirect('/login')




app = webapp2.WSGIApplication([('/signup', SignUp),
                            ('/welcome', WelcomeHandler),
                            ('/login', LoginHandler),
                            ('/blog/newpost', NewPost),
                            ('/blog', MainPage),
                            ('/', MainPage),
                            ('/blog/([0-9]+)', Permalink),
                            ('/logout', Logout),
                            ('/blog/([0-9]+)/edit', Editpost),
                            ('/editcomments/([0-9]+)/([0-9]+)', EditComment),
                            ('/delcomment/([0-9]+)/([0-9]+)', DeleteComment),
                            ('/delpost/([0-9]+)', DeletePost),
                            ('/rate/([0-9]+)/([0-9]+)', RatePost)],
                             debug = True)








