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

    def get(self):
        keys = self.request.arguments()
        if keys.count('callback') > 0:
            self.post()
            return

        self.error(400)
        self.response.out.write('callback is required.')
        return

    def default_content_type(self):
        return 'text/plain'

    def write_data(self, data):
        json = simplejson.dumps(data, ensure_ascii=False)
        content_type = 'application/json'
        callback = self.request.get('callback')
        if callback:
            content = callback + '(' + json + ');'
            content_type = 'text/javascript'
        else:
            content = json

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(content)
        return


    def write_standard_data(self, data):
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        self.write_data({ 'data': data, 'namespace': namespace})

    def set_or_add(self, method): # method = set or add
        if self.request.arguments().count('set') or self.request.arguments().count('add'):
            self.error(500)
            self.response.out.write('Internal Server Error')
            return

        data = {}
        keys = self.request.arguments()
        if keys.count('expire') > 0: keys.remove('expire')
        if keys.count('namespace') > 0: keys.remove('namespace')
        if keys.count('callback') > 0: keys.remove('callback')
        for key in keys:
            data[key] = self.request.get(key)

        if len(data) == 0:
            self.error(400)
            self.response.out.write('data is required(example: ?foo=bar')
            return

        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: %s", namespace)
        callback = self.request.get('callback')

        expire = 0

        if self.request.get('expire'):
            try:
                expire = int(self.request.get('expire'))
                if expire < 0:
                    self.error(400)
                    self.response.out.write('expire must >= 0')
                    return
                
            except ValueError, message:
                self.error(400)
                self.response.out.write('expire must >= 0')
                return

        logging.info("expire: %s", expire)

        update_method = getattr(memcache, method)
        for key in data.keys():
            logging.info("%s key: %s", method, key)
            res = update_method(key, data[key], expire, 0, namespace)
            logging.info("value: %s", data[key])
            logging.info("result: %s", res)
            if method == 'add': data[key] = res

        self.write_standard_data(data)

    def incr_or_decr(self, method):
        if self.request.arguments().count('incr') or self.request.arguments().count('decr'):
            self.error(500)
            self.response.out.write('Internal Server Error')
            return
        data = {}
        namespace = self.request.get('namespace')
        callback = self.request.get('callback')
        delta = self.request.get('delta')

        if delta:
            try:
                delta = int(delta)
                if delta < 0:
                    self.error(400)
                    self.response.out.write('delta must > 0')
                    return
            except ValueError, message:
                self.error(400)
                self.response.out.write('delta must be int')
                return
        else:
            delta = 1

        logging.info("namespace: %s", namespace)
        logging.info("delta: %d", delta)

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        update_method = getattr(memcache, method)
        for key in keys:
            logging.info("%s key: %s", method, key)
            data[key] = update_method(key, delta, namespace)

        self.write_standard_data(data)

    
class GetHandler(Helper):
    def get(self):
        data = { }
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: %s", namespace)
        callback = self.request.get('callback')

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        for key in keys:
            logging.info("get key: %s", key)
            data[key] = memcache.get(key, namespace)
            logging.info("value: %s", data[key])

        self.write_standard_data(data)

class SetHandler(Helper):
    def post(self):
        self.set_or_add('set')
        return

class AddHandler(Helper):
    def post(self):
        self.set_or_add('add')
        return

class DeleteHandler(Helper):
    def post(self):
        data = { }
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: %s", namespace)

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        for key in keys:
            logging.info("delete key: %s", key)
            memcache.delete(key, 0, namespace)
            data[key] = None

        self.write_standard_data(data)

class StatsHandler(Helper):
    def get(self):
        logging.info("get stats")
        data = memcache.get_stats()
        self.write_data(data)

class IncrHandler(Helper):
    def post(self):
        self.incr_or_decr('incr')

class DecrHandler(Helper):
    def post(self):
        self.incr_or_decr('decr')

class RawHandler(Helper):
    def get(self):
        namespace = self.request.get('namespace')
        if not namespace: namespace = self.default_namespace()
        logging.info("namespace: (%s)", namespace)
        callback = self.request.get('callback')

        key = self.request.get('key')
        logging.info("get key: %s", key)
        result = memcache.get(key, namespace)
        logging.info("value: %s", key)

        content_type = self.request.get('content_type')
        if not content_type: content_type = self.default_content_type()
        logging.info("content_type: %s", content_type)

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return
