import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson
import urllib

class Helper(webapp.RequestHandler):
    def default_namespace(self):
        return 'default'

class GetHandler(Helper):
    def get(self):
        data = { }
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: (%s)", namespace)

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        for key in keys:
            logging.info("get key: (%s)", key)
            data[key] = memcache.get(key, namespace)

        result = simplejson.dumps(
            data,
            ensure_ascii=False
            )

        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(result)
        return

class SetHandler(Helper):
    def post(self):
        data = {}
        keys = self.request.arguments()
        if keys.count('expire') > 0: keys.remove('expire')
        if keys.count('namespace') > 0: keys.remove('namespace')
        for key in keys: data[key] = self.request.get(key)

        if len(data) == 0:
            self.error(400)
            self.response.out.write('data is required(example: ?foo=bar')
            return

        expire = self.request.get('expire')
        namespace = self.request.get('namespace')
        logging.info("namespace: (%s)", namespace)

        if not namespace: namespace = self.default_namespace()
        if expire:
            try:
                expire = int(expire)
                if expire <= 0:
                    self.error(400)
                    self.response.out.write('expire must > 0')
                    return
                
            except ValueError, message:
                self.error(400)
                self.response.out.write('expire must > 0')
                return
        else:
            expire = 3600 * 24

        logging.info("expire: (%s)", expire)

        for key in data.keys():
            logging.info("set key: (%s)", key)
            memcache.set(key, data[key], expire, 0, namespace)

        result = simplejson.dumps(
            data,
            ensure_ascii=False
            )

        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(result)
        return

class DeleteHandler(Helper):
    def post(self):
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: (%s)", namespace)

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        for key in keys:
            logging.info("delete key: (%s)", key)
            memcache.delete(key, 0, namespace)
        
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write({ })
        return

class StatsHandler(Helper):
    def get(self):
        logging.info("get stats")
        data = memcache.get_stats()

        result = simplejson.dumps(
            data,
            ensure_ascii=False
            )

        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(result)
        return
