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

        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

class SetHandler(Helper):
    def post(self):
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

        expire = self.request.get('expire')
        namespace = self.request.get('namespace')
        logging.info("namespace: %s", namespace)
        callback = self.request.get('callback')

        if not namespace: namespace = self.default_namespace()
        if expire:
            try:
                expire = int(expire)
                if expire < 0:
                    self.error(400)
                    self.response.out.write('expire must >= 0')
                    return
                
            except ValueError, message:
                self.error(400)
                self.response.out.write('expire must >= 0')
                return
        else:
            expire = 3600 * 24

        logging.info("expire: %s", expire)

        for key in data.keys():
            logging.info("set key: %s", key)
            memcache.set(key, data[key], expire, 0, namespace)
            logging.info("value: %s", data[key])


        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

    def get(self):
        keys = self.request.arguments()
        if keys.count('callback') > 0:
            self.post()
            return
        
        self.error(400)
        self.response.out.write('data is required(example: ?foo=bar')
        return

class AddHandler(Helper):
    def post(self):
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

        expire = self.request.get('expire')
        namespace = self.request.get('namespace')
        logging.info("namespace: %s", namespace)
        callback = self.request.get('callback')

        if not namespace: namespace = self.default_namespace()
        if expire:
            try:
                expire = int(expire)
                if expire < 0:
                    self.error(400)
                    self.response.out.write('expire must >= 0')
                    return
                
            except ValueError, message:
                self.error(400)
                self.response.out.write('expire must >= 0')
                return
        else:
            expire = 3600 * 24

        logging.info("expire: %s", expire)

        for key in data.keys():
            logging.info("add key: %s", key)
            res = memcache.add(key, data[key], expire, 0, namespace)
            logging.info("value: %s", data[key])
            logging.info("result: %s", res)
            data[key] = res


        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

    def get(self):
        keys = self.request.arguments()
        if keys.count('callback') > 0:
            self.post()
            return
        
        self.error(400)
        self.response.out.write('data is required(example: ?foo=bar')
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

        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        callback = self.request.get('callback')
        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

class StatsHandler(Helper):
    def get(self):
        logging.info("get stats")
        data = memcache.get_stats()

        result = simplejson.dumps(
            data,
            ensure_ascii=False
            )

        callback = self.request.get('callback')
        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

class IncrHandler(Helper):
    def post(self):
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
        for key in keys:
            logging.info("incr key: %s", key)
            data[key] = memcache.incr(key, delta, namespace)

        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

class DecrHandler(Helper):
    def post(self):
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

        logging.info("namespace: (%s)", namespace)
        logging.info("delta: %d", delta)

        keys = self.request.get_all('key')
        keys.extend(self.request.get_all('key[]'))
        for key in keys:
            logging.info("decr key: %s", key)
            data[key] = memcache.decr(key, delta, namespace)

        result = simplejson.dumps(
            { 'data': data, 'namespace': namespace},
            ensure_ascii=False
            )

        content_type = 'application/json'
        if callback:
            result = callback + '(' + result + ');'
            content_type = 'text/javascript'

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(result)
        return

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
