import webapp2
import re

form_validation = '''
<form method="post">
	<input type="text" name="username" placeholder="username"><div>%(i_username)s</div>
	<input type="password" name="password" placeholder="password"><div>%(i_password)s</div>
	<input type="password" name="verify" placeholder="verify password"><div>%(i_verify)s</div>
	<input type="text" name="email" placeholder="email"><div>%(i_email)s</div>
	<input type="submit">
'''

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class ValidationHandler(webapp2.RequestHandler):

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
		self.response.out.write(form_validation %
			{'i_username': i_username, 'i_password': i_password,
			'i_verify': i_verify, 'i_email': i_email})

	def get(self):
		self.i_username = self.i_password = self.i_verify = self.i_email = ""
		self.renderForm(self.i_username, self.i_password, self.i_verify, self.i_email)

	def post(self):
		self.i_username = self.i_password = self.i_verify = self.i_email = ""
		invalid_field = False

		if self.validateInput(self.request.get('username'), USER_RE):
			self.i_username = "That's not a valid username, bro."
			invalid_field = True
		if self.validateInput(self.request.get('password'), PASS_RE):
			self.i_password = "That's not a valid password, bro."
			invalid_field = True
		if self.matchPassword(self.request.get('password'), self.request.get('verify')):
			self.i_verify = "Your passwords don't match. Sucks."
			invalid_field = True
		if self.request.get('email') != "" and self.validateInput(self.request.get('email'), EMAIL_RE):
			self.i_email = "We need to spam you."
			invalid_field = True

		if not invalid_field:
			self.redirect("/validation/thanks?username=" + self.request.get('username'))
		else:
			self.renderForm(self.i_username, self.i_password, self.i_verify, self.i_email)

class ValidationThanksHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("Welcome, %s!" % self.request.get('username'))