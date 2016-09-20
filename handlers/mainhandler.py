import jinja2
import webapp2
from models import BlogInfo, Likes, User, Comment
import main


# functions for jinja2 to display template html files
class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = main.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_user(self):
        user_cookie_str =self.request.cookies.get("user_id")
        if user_cookie_str:
            cookie_val = main.check_secure_val(user_cookie_str)
            if cookie_val:
                this_user = User.get_by_id(int(cookie_val))
                return this_user.username