import webapp2
from mainhandler import Handler

# Set cookie to nothing to logout
class Logout(Handler):

    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id =; Path=/')
        self.redirect('/login')