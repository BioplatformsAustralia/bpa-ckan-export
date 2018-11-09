import logging
import ckanapi
import string
import requests
import os


def make_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] [%(threadName)s]  %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger


def make_ckan_api(args):
    ckan = ckanapi.RemoteCKAN(args.ckan_url, apikey=args.api_key)
    return ckan


def make_registration_decorator():
    """
    returns a (decorator, list). any function decorated with
    the returned decorator will be appended to the list
    """
    registered = []

    def _register(fn):
        registered.append(fn)
        return fn

    return _register, registered


CKAN_AUTH = {
    'login': 'CKAN_USERNAME',
    'password': 'CKAN_PASSWORD'
}


# http://stackoverflow.com/questions/38271351/download-resources-from-private-ckan-datasets
def authenticated_ckan_session(ckan):
    s = requests.Session()
    data = dict((k, os.environ.get(v)) for k, v in CKAN_AUTH.items())
    if any(t is None for t in data.values()):
        raise Exception('please set %s' % (', '.join(CKAN_AUTH.values())))
    url = ckan.address + '/login_generic'
    r = s.post(url, data=data)
    if 'field-login' in r.text:
        raise RuntimeError('Login failed.')
    return s


def safe_path(parts):
    def escape(s):
        s = s.lower().strip()
        l = []
        for t in s:
            if t in string.digits or t in string.ascii_letters or t == '-' or t == '_':
                l.append(t)
            else:
                l.append('_')
        return ''.join(l)
    return '/'.join([escape(t) for t in parts])
