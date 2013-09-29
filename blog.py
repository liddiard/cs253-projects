import webapp2
import main
from google.appengine.ext import db
from google.appengine.api import memcache
import time, logging, json

# Models

class Post(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)

# Views

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = main.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def setQueryTime(self):
        last_queried = memcache.get('last_queried')
        if last_queried is None:
            memcache.add('last_queried', int(time.time()))
        else:
            memcache.set('last_queried', int(time.time()))

    def getQueryTime(self):
        last_queried = memcache.get('last_queried')
        if last_queried is None:
            return
        else:
            return int(time.time()) - last_queried

class Front(Handler):
    def get(self):
        posts = memcache.get('front')
        if posts is None:
            posts = list(Post.all().order("-created").run(limit=10))
            logging.error("DB query")
            self.setQueryTime()
            memcache.add('front', posts)
        self.render("blog_front.html", posts=posts, last_queried=self.getQueryTime())

class ViewPost(Handler):
    def get(self, post_id):
        cached = memcache.get('post-%s' % post_id)
        if cached is None:
            post = Post.get_by_id(int(post_id))
            logging.error("DB query")
            self.setQueryTime()
            key = "post-%s" % post_id
            memcache.add(key, post)
        else:
            post = cached
        self.render("blog_post.html", post=post, last_queried=self.getQueryTime())

class NewPost(Handler):
    def get(self):
        self.render("blog_newpost.html", template_dir="templates")

    def post(self):
        title = self.request.get("subject")
        body = self.request.get("content")

        if title and body:
            p = Post(title=title, body=body)
            p_key = p.put()
            time.sleep(.1) #this is bad
            posts = list(Post.all().order("-created").run(limit=10))
            logging.error("DB query")
            self.setQueryTime()
            memcache.set('front', posts)
            self.redirect("/blog/%s" % p_key.id())
        else:
            error = "You must enter a title and post content."
            self.render("blog_newpost.html", template_dir="templates",
                    title=title, body=body, error=error)

class JsonFront(Handler):
    def get(self):
        obj = []
        posts = Post.all().order("-created").run(limit=10)
        for post in posts:
            p = {"subject": post.title, "content": post.body, "created": post.created.strftime("%a %d %B %Y")}
            obj.append(p)
        self.response.headers['Content-Type'] = 'application/json'
        self.write(json.dumps(obj))

class JsonViewPost(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        p = {"subject": post.title, "content": post.body, "created": post.created.strftime("%a %d %B %Y")}
        self.response.headers['Content-Type'] = 'application/json'
        self.write(json.dumps(p))

class FlushCache(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect('/blog')