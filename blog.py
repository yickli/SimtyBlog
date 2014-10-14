import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import markdown2
import os

# import libarary
import pymongo

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    """use self.application.db to call"""
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            #(r"/archive", ArchiveHandler),
            #(r"/gallery", GalleryHandler),
            (r"/admin", AdminHandler),
            #(r"/tags", TagsHandler),
            (r"/user/login", LoginHandler),
            #(r"/user/logout", LogoutHandler),
            (r"/blog/([^/]+)", BlogHandler),
            (r"/del/([^/]+)", BlogDelHandler),
            (r"/register", RegisterHandler),
            
            #(r"/search", SearchHandler),
        ]
        settings = dict(
            blog_title = u"YujieLee",
            blog_description = u"A blog which is powerd by Tornado and Mongodb.",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            #ui_module = {"Blog" : BlogModule},
            xsrf_cookie = True,
            cookie_secret = "V}D7:[vrj#",
            #login_url = "user/login",
            #debug = True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        # Have one global connection to the blog DB across all handlers
        conn = pymongo.Connection("localhost", 27017)
        self.db = conn["example"]

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    def get_current_user(self):
        user = self.get_secure_cookie("woleigedaca")
        if not user:
            return None
        return self.db.users.find_one({"name" : user})

class HomeHandler(BaseHandler):
    def get(self):
        blogs = self.db.blogs.find()
        name = self.get_secure_cookie('woleigedadca')
        self.render("index.html", blogs = blogs, ckname = name)
    def post(self):
        name = self.get_argument("name")
        pwd = self.get_argument("password")
        res = check(name, pwd)
        if res:
            self.set_secure_cookie('woleigedadca', name)
            self.redirect("/")
        else:
            self.redirect("/user/login")

class LoginHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        self.render("login.html")
    def post(self):
        coll = self.db.users
        name = self.get_argument("username")
        pwd = self.get_argument("password")
        
        res = check(coll, name, pwd)
        if res:
            self.set_secure_cookie('woleigedadca', name)
            self.redirect("/")
        else:
            self.redirect("/user/login")

class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        coll = self.db.users
        name = self.get_argument("username")
        pwd = self.get_argument("password")

        res = check(coll, name)
        if res:
            self.redirect("/register")
        else:
            coll.insert({'name' : name, 'password' : pwd})
            self.set_secure_cookie('woleigedadca', name)
            self.redirect("/")

def check(coll, name, pwd = None):
    if not pwd:
        for i in coll.find():
            if name == i['name']:
                return True
        return False
    else:
        for i in coll.find():
            if name == i['name']:
                if pwd == i['password']:
                    return True
                else:
                    return False
        return False

class AdminHandler(BaseHandler):
    def get(self):
        name = self.get_secure_cookie("woleigedadca")
        self.render("admin.html", cookieName = name)
    def post(self):
        title = self.get_argument('title')
        blog = self.get_argument('blog')
        name = self.get_secure_cookie('woleigedadca')
        self.db.blogs.insert({'name': name, 'text': blog, 'title': title})
        self.redirect('/blog/'+str(title))

class BlogHandler(BaseHandler):
    def get(self, title):
        name = self.get_secure_cookie("woleigedadca")
        blog = self.db.blogs.find_one({'title': title})
        self.render("blog.html", cookieName = name, blog = blog)

class BlogDelHandler(BaseHandler):
    def get(self, title):
        self.db.blogs.remove({'title': title})
        self.redirect('/')
#class CommentHandler(BaseHandler):
#    def post(self):


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()    