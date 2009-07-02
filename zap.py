from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from urlparse import urlsplit, urlunsplit
from urllib import unquote
from logging import info
from gen import next


class Entry(db.Model):
    author = db.UserProperty()
    url = db.StringProperty()
    zap = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)


class Friend(db.Model):
    email = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)


class NotHere(webapp.RequestHandler):

    def get(self):
        self.error(404)


class Zap(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        write = self.response.out.write
        url = self.request.get('url')
        assert url, 'no url?'
        entry = Entry.gql('where url = :url', url=url).get()
        if entry is None:
            user = users.get_current_user()
            if user is None:
                self.redirect(users.create_login_url(self.request.uri))
                return
            email = user.email()
            friend = Friend.gql('where email = :email', email=email).get()
            if friend is None:
                info('prevented %s from zapping %s', email, url)
                write('not allowed')
                return
            query = Entry.gql('order by date desc')
            last = query.get()
            if last is not None:
                zap = next(last.zap)
            else:
                zap = next('')
            entry = Entry()
            entry.author = user
            entry.url = url
            entry.zap = zap
            entry.put()
            info('zapped %s to %s for user %s', url, zap, user)
        base = urlsplit(self.request.uri)
        host = urlunsplit(base[:2] + ('/', '', ''))
        target = host + entry.zap
        write('zapped (%d chars): %s <br/>' % (len(url), url))
        write('to (%d chars): <a href="%s">%s</a> <br/>' % (len(target),
            target, target))


class Unzap(webapp.RequestHandler):

    def get(self, zap):
        self.response.headers['Content-Type'] = 'text/plain'
        entry = Entry.gql('where zap = :zap', zap=unquote(zap)).get()
        if entry is None:
            self.error(404)
            self.response.out.write('doh!')
            info('request for unknown zap: /%s', zap)
        else:
            self.redirect(entry.url)
            info('redirecting /%s to %s', zap, entry.url)


class Friends(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        write = self.response.out.write
        email = self.request.get('email')
        assert email, 'no email?'
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return
        friend = Friend.gql('where email = :email', email=email).get()
        if friend is None:
            friend = Friend()
            friend.email = email
            friend.put()
            user = users.get_current_user()
            msg = '%s added %s as a friend' % (user.email(), email)
        else:
            msg = '%s already exists as a friend' % email
        info(msg)
        write(msg)


application = webapp.WSGIApplication([
    ('/favicon.ico', NotHere),
    ('/create', Zap),
    ('/friends', Friends),
    (r'/(.*)', Unzap)],
    debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
