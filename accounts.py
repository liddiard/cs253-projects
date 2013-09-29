import re, hmac
import webapp2, main
from google.appengine.ext import db

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

# MODELS

class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.StringProperty(required=False)

# VIEWS

class ValidationHandler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = main.jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def validateInput(self, field, regex):
		if regex.match(field):
			return False
		else:
			return True

	def matchPassword(self, password1, password2):
		if password1 == password2:
			return False
		else: 
			return True

	def renderForm(self, i_username, i_password, i_verify, i_email):
		self.render("accounts_register.html", i_username=i_username, i_password=i_password,
			i_verify=i_verify, i_email=i_email)

	def hashStr(self, s):
		secret = "fVVKLgraoD"
		return hmac.new(secret, s).hexdigest()

	def makeSecureVal(self, s):
		return "%s|%s" % (s, self.hashStr(s))

	def checkSecureVal(self, comboVal):
		val = comboVal.split('|')[0]
		if comboVal == self.makeSecureVal(val):
			return val

	def get(self):
		i_username = i_password = i_verify = i_email = ""
		self.renderForm(i_username, i_password, i_verify, i_email)

	def post(self):
		i_username = i_password = i_verify = i_email = ""
		invalid_field = False

		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')

		if self.validateInput(username, USER_RE):
			i_username = "Please enter a vaild username."
			invalid_field = True
		users = User.all().filter("username =", username)
		try:
			if users.get().username == username:
				i_username = "That user already exists."
				invalid_field = True
		except AttributeError:
			pass
		if self.validateInput(password, PASS_RE):
			i_password = "Please enter a vaild password."
			invalid_field = True
		if self.matchPassword(password, verify):
			i_verify = "Your passwords don't match."
			invalid_field = True
		if email != "" and self.validateInput(email, EMAIL_RE):
			i_email = "Please enter a valid email address."
			invalid_field = True

		if not invalid_field:
			cookie_combo = self.makeSecureVal(username)
			self.response.headers.add_header(str('Set-Cookie'), str('username='+cookie_combo+'; Path=/'))
			self.redirect("/blog/welcome")
		else:
			u = User(username=username, password=password, email=email)
			u.put()
			self.renderForm(i_username, i_password, i_verify, i_email)

validation_handler = ValidationHandler()

class ValidationSignupHandler(webapp2.RequestHandler):
	def get(self):
		if validation_handler.checkSecureVal(self.request.cookies.get('username')):
			user = self.request.cookies.get('username').split('|')[0]
			self.response.out.write("Welcome, %s!" % user)
		else:
			self.redirect("/blog/signup")

class LoginHandler(ValidationHandler):
	def get(self):
		self.render("accounts_login.html")

	def post(self):
		q = User.all().filter('username =', self.request.get('username')).get()
		if q and self.request.get('password') == q.password:
			self.redirect("/blog/welcome")
		else:
			invalid = "Please enter a valid username and password."
			self.render("accounts_login.html", invalid=invalid)

class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers.add_header(str('Set-Cookie'), str('username=; Path=/'))
		self.redirect("/blog/signup")