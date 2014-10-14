import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import markdown

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
            (r"/register", RegisterHandler),
            #(r"/search", SearchHandler),
        ]
        settings = dict(
            #blog_title = u"YujieLee",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            #ui_module = {"Blog" : BlogModule},
            #xsrf_cookie = True,
            #cookie_secret = "V}D7:[vrj#",
            #login_url = "user/login",
            #debug = True,
        )
        conn = pymongo.Connection("localhost", 27017)
        self.db = conn["blogweb"]
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def db(self):
        return self.application.db
    def get_current_user(self):
        user_id = self.get_secure_cookie("woleigedaca")
        if not user_id:
            return None
        return self.db.authors.find_one("user_id" : user_id)

class HomeHandler(BaseHandler):
    def get(self):
        name = self.get_cookie('woleigedaca')
        blogs = showAllBlogs()
        self.render("index.html", cookieName = name, blogs = blogs)
    def post(self):
        name = self.get_argument("name")
        pwd = self.get_argument("password")
        res = check(name, pwd)
        if res:
            self.set_cookie('woleigedadca', name)
            self.redirect("/")
        else:
            self.redirect("/login")

def showAllBlogs():
    coll = self.application.db.blogs
    tmp = coll.find()
    return tmp[::-1] 

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        name = self.get_argument("name")
        pwd = self.get_argument("password")
        res = check(name, pwd)
        if res:
            self.set_cookie('woleigedadca', name)
            self.redirect("/")
        else:
            self.redirect("/login")

class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        coll = self.application.db.users
        name = self.get_argument("username")
        pwd = self.get_argument("password")
        res = check(name)
        if res:
            self.redirect("/register")
        else:
            coll.insert({name : name}, {password : pwd})
            self.set_cookie('woleigedadca', name)
            self.redirect("/")

def check(name, pwd = None):
    coll = self.application.db.users
    if not pwd:
        for i in coll.find(name):
            if name == i[1]:
                return True
        return False
    else:
        for i in coll.find(name):
            if name == i[1]:
                if pwd == i[2]:
                    return True
                else:
                    return False
        return False

class AdminHandler(BaseHandler):
    def get(self):
        name = get_cookie("woleigedadca")
        self.render("admin.html", cookieName = name)
    def post(self):
        title = self.get_argument("title")
        blog_md = self.get_argument("blog")
        blog = translate(blog_md)
        name = get_cookie("woleigedadca")
        coll = self.application.db.blogs
        coll.insert(name, title, blog)
        self.redirect("/blog/"+str(idvalue))

def translate(md):  
    for i in whiteList:  
        if i[0] in md:  
            md=md.replace(i[0],i[1])  
    md2=html.escape(md)  
    data=markdown2.markdown(md2)  
    for i in whiteList:  
        if i[1] in data:  
            data=data.replace(i[1],i[0])  
    return data 

class BlogHandler(BaseHandler):
    def get(self, idvalue):
        name = get_cookie("woleigedadca")
        blog = showOneBlog(idvalue)
        self.render("blog.html", cookieName = name, blog = blog, comments = comments)

class CommentHandler(BaseHandler):
    def post(self):


class Handler(tornado.web.RequestHandler):
    def get(self, word):
        coll = self.application.db.words
        word_doc = coll.find_one({"word": word})
        if word_doc:
            del word_doc["_id"]
            self.write(word_doc)
        else:
            self.set_status(404)
            self.write({"error": "word not found"})
    
    def post(self, word):
        definition = self.get_argument("definition")
        coll = self.application.db.words
        word_doc = coll.find_one({"word": word})
        if word_doc:
            word_doc["definition"] = definition
            coll.save(word_doc)
        else:
            word_doc = {"word": word, "definition": definition}
            coll.insert(word_doc)
        del word_doc["_id"]
        self.write(word_doc)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
