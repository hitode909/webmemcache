from google.appengine.ext import webapp
from handlers import *

def main():
  application = webapp.WSGIApplication(
    [
      (r'/stats',  StatsHandler),
      (r'/set',    SetHandler),
      (r'/add',    AddHandler),
      (r'/get',    GetHandler),
      (r'/delete', DeleteHandler),
      (r'/incr',   IncrHandler),
      (r'/decr',   DecrHandler),
      (r'/raw',    RawHandler),
      ],
    debug=True)

  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
