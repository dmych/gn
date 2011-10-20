# This file is part of Geeky Notes
# 
# Geeky Notes is a CLI Simplenote client
# <https://github.com/dmych/gn>
# 
# Copyright (c) Dmitri Brechalov, 2010-2011
# 
# Geeky Notes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Geeky Notes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

'''Geeky Notes - Simplenote CLI client
api.py: simplenote API implementation
'''

import base64
import logging
import urllib
import urllib2

VERBOSE_DEBUG = False

# as suggested in  http://groups.google.com/group/simplenote-api/msg/d82541d58e7109f8
escape_table = (  
    ('#', '%23'), 
#    ('$', '%24'),
    ('%', '%25'),
    ('+', '%2b'),
    ('&', '%26'),
    (';', '%3b'),
    ('^', '%5e'),
    ('~', '%7e'),
    )

def dbg(msg):
    if not VERBOSE_DEBUG: return
    from sys import stderr
    stderr.write('**** %s\n' % (msg))

def dbg2(msg):
    from sys import stderr
    stderr.write('**** %s\n' % (msg))

try:
    import json
except ImportError:
    import simplejson as json

VERSION = "0.4"

USER_AGENT = "Geeky Notes/%s" % (VERSION)

class SimplenoteError(Exception):
    def __init__(self, method, msg):
        self.method = method
        self.msg = msg

    def __repr__(self):
        return "%s: [%s] %r" % (self.__class__.__name__, self.method, self.msg)

class SimplenoteAuthError(SimplenoteError):
    def __init__(self, email, msg):
        self.email = email
        self.method = "auth"
        self.msg = msg

class Simplenote(object):
    '''Simplenote API 2
    '''
    api_url = "https://simple-note.appspot.com/api/"
    api2_url = "https://simple-note.appspot.com/api2/"

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.login()
	self._index = None

    def _getAuth(self):
        return 'auth=%s&email=%s' % (self._token, urllib.quote(self.email))

    def _s(self, d):
	r = dict()
	for k, v in d.items():
	    if type(k) == type(u''):
		k = k.encode('utf-8')
	    if type(v) == type(u''):
		v = v.encode('utf-8')
	    dbg('%s = %s' % (k, v))
	    r[k] = v
	return r

    def login(self):
	'''Login to simplenote
	'''
        url = self.api_url + 'login'
        credentials = {
            'email': self.email,
            'password': self.password
	    }
        data = base64.b64encode(urllib.urlencode(credentials))
	dbg('LOGIN: ' + url)
        res = urllib.urlopen(url, data)
        self._token = res.read().strip()
        return self._token

    def _getIndexPortion(self, mark=None, **kwargs):
	'''Get raw response with portion of index from Simplenote
	'''
        args = '&'.join([ '%s=%s' % (k, v) for k, v in kwargs.items() ])
	if args:
	    args = '&' + args
        url = '%sindex?%s%s' % (self.api2_url, self._getAuth(), args)
	dbg(url)
	if mark is not None:
	    url += '&mark=%s' % (mark)
	#dbg2('INDEX: ' + url)
        res = urllib.urlopen(url)
        response = json.loads(res.read().replace('\t', '\\t'))
	dbg('RESPONSE:\n' + repr(response))
	return response

    def index(self, **kwargs):
	'''Return the index (optional API args length etc allowed)
	'''
	response = self._getIndexPortion(**kwargs)
	self._index = list()
	while True:
	    for rec in response['data']:
		self._index.append(self._s(rec))
	    if not response.has_key('mark'):
		break
	    response = self._getIndexPortion(response['mark'], **kwargs)
        return self._index

    def keys(self):
	'''Return dictionary with {key: index_item}
	'''
	result = dict()
	if self._index is None:
	    self.index()
	for item in self._index:
	    result[item['key']] = item
	return result

    def get(self, key):
	'''Retrieve a note with the given key
	'''
        url = self.api2_url + 'data/' + key + '?' + self._getAuth()
        res = urllib.urlopen(url)
	try:
	    resp = res.read().replace('\t', '\\t')
	    return self._s(json.loads(resp))
	except ValueError, details:
	    print 'ERROR:', details
	    print resp

    def update(self, data):
	'''Store the note to simplenote
	Create a new note if no "key" field specified,
	or update existent one otherwise.
	Return updated note's contents
	'''
        url = self.api2_url + 'data'
	if data.has_key('key'):
	    url += '/%s' % (data['key'])
	url += '?' + self._getAuth()
	edt = data.copy()
	cnt = edt['content']
	for c, v in escape_table:
	    cnt = cnt.replace(c, v)
	edt['content'] = cnt
	edata = json.dumps(edt)
	dbg('TYPE (data):  ' + str(type(data)))
	dbg('TYPE (edata): ' + str(type(edata)))
	dbg('UPDATE: ' + url)
	dbg('        ' + edata)
	dbg('--------')
	res = urllib.urlopen(url, edata)
	result = data.copy()
	try:
	    resp = res.read().replace('\t', '\\t')
	    result.update(self._s(json.loads(resp)))
	except ValueError, details:
	    print 'ERROR:', details
	    print resp
	return result
