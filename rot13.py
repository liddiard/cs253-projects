import webapp2
from cgi import escape

form_rot13 = '''
<form method="post">
	<textarea name="text" placeholder="Enter text to ROT13">%(contents)s</textarea>
	<br/>
	<input type="submit">
</form>
'''

class Rot13Handler(webapp2.RequestHandler):
	def write_form(self, contents=""):
		self.response.out.write(form_rot13 % {'contents': contents})

	def get(self):
		self.write_form()

	def post(self):
		plaintext = self.request.get('text')
		encrypted = plaintext.encode('rot13')
		self.write_form(escape(encrypted, True))