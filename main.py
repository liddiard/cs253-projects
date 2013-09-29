#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import rot13, validation, blog, accounts

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

mainPage = '''
<h1 style="font-family: sans-serif">CS253 Projects</h1>
'''

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(mainPage)

# URLs

app = webapp2.WSGIApplication([
    ('/', MainHandler),

    # validation
    ('/rot13/?', rot13.Rot13Handler),
    ('/validation/?', validation.ValidationHandler), 
    ('/validation/thanks/?', validation.ValidationThanksHandler),

    # blog
    ('/blog/?', blog.Front),
    ('/blog/\.json/?', blog.JsonFront),
    ('/blog/newpost/?', blog.NewPost),
    ('/blog/(?P<post_id>\d+)/?', blog.ViewPost),
    ('/blog/(?P<post_id>\d+)\.json/?', blog.JsonViewPost),
    ('/blog/flush', blog.FlushCache),

    # accounts
    ('/blog/signup/?', accounts.ValidationHandler),
    ('/blog/welcome/?', accounts.ValidationSignupHandler),
    ('/blog/login/?', accounts.LoginHandler),
    ('/blog/logout/?', accounts.LogoutHandler)
], debug=True)