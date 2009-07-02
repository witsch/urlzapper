from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from urllib import unquote
from gen import next


class Entry(db.Model):
    author = db.UserProperty()
    url = db.StringProperty()
    zap = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)


class NotHere(webapp.RequestHandler):

    def get(self):
        self.error(404)


class Zap(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        url = self.request.get('url')
        assert url, 'no url?'
        entry = Entry.gql('where url = :url', url=url).get()
        if entry is None:
            query = Entry.gql('order by date desc')
            last = query.get()
            if last is not None:
                zap = next(last.zap)
            else:
                zap = next('')
            entry = Entry()
            entry.author = users.get_current_user()
            entry.url = url
            entry.zap = zap
            entry.put()
        write = self.response.out.write
        write('zapped: %s (%d chars) <br/>' % (entry.url, len(entry.url)))
        write('to:     %s (%d chars) <br/>' % (entry.zap, len(entry.zap)))


class Unzap(webapp.RequestHandler):

    def get(self, zap):
        self.response.headers['Content-Type'] = 'text/plain'
        entry = Entry.gql('where zap = :zap', zap=unquote(zap)).get()
        if entry is None:
            self.error(404)
            self.response.out.write('doh!')
        else:
            self.redirect(entry.url)


application = webapp.WSGIApplication([
    ('/favicon.ico', NotHere),
    ('/create', Zap),
    (r'/(.*)', Unzap)],
    debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
