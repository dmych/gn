# db.py: local database implementation

'''This is a part of gn project
gn (Geeky Notes) is a CLI Simplenote client
https://github.com/dmych/gn
Copyright (c) Dmitri Brechalov, 2010-2011
'''

import shelve
import os
import time

DATAFILE = os.path.expanduser('~/.gn.db')

## Note format according to the API:
## {
##    key:        (string, note identifier, created by server),
##    deleted:    (bool, whether or not note is in trash),
##    modifydate: (last modified date, in seconds since epoch),
##    createdate: (note created date, in seconds since epoch),
##    syncnum:    (integer, number set by server, track note changes),
##    version:    (integer, number set by server, track note content changes),
##    minversion: (integer, number set by server, minimum version available for note),
##    sharekey:   (string, shared note identifier),
##    publishkey: (string, published note identifier),
##    systemtags: [ (Array of strings, some set by server) ],
##    tags:       [ (Array of strings) ],
##    content:    (string, data content)
## }

## Our own fields:
##    CHANGED:  (bool, did the note changed locally?)

KEY_PREFIX = 'SIMPLA_'

class Database(object):
    '''Local simplenote database based on shelve storage

    New notes which are not synced have no key field.
    Instead a temporary key is used to identify them in the index.
    '''
    def __init__(self, fname=None):
        if fname is None:
            fname = DATAFILE
        self.db = shelve.open(fname)

    def _getTemporaryKey(self):
	return KEY_PREFIX + str(time.time())

    def _getKeys(self, deleted=False):
	if deleted:
	    keys = self.db.keys()
	else:
	    keys = [k for k in self.db.keys() if self.db[k]['deleted'] == 0]
	return keys

    def values(self):
	return self.db.values()

    def index(self, sort=None, reverse=True, deleted=False):
	def srt(n1, n2):
	    n1m = float(n1['modifydate'])
	    n2m = float(n2['modifydate'])
	    if n1m < n2m: return -1
	    if n1m > n2m: return 1
	    return 0
	result = list()
        keys = self._getKeys(deleted)
	if sort == True:
	    sort = srt
	for k in keys:
	    rec = self.get(k)
	    del rec['content']
	    result.append(rec)
	result.sort(cmp=sort, reverse=reverse)
        return result

    def keys(self, sort=None, reverse=True, deleted=False):
	result = [ item['key'] for item in self.index(sort, reverse, deleted) ]
	return result

    def get(self, key):
	return self.db[key]

    def update(self, data):
	if data.has_key('key') and data['key'].startswith(KEY_PREFIX):
	    del data['key']
	if not data.has_key('key'):
	    key = self._getTemporaryKey()
	    data['key'] = key
	else:
	    key = data['key']
	if not data.has_key('CHANGED'):
	    data['CHANGED'] = False
	self.db[key] = data
	self.db.sync()

    def replace(self, oldkey, data):
	newkey = data['key']
	self.db[newkey] = data
	self.remove(oldkey)

    def remove(self, key):
	del self.db[key]
	self.db.sync()

class Note(object):
    '''Note implementetion
    '''
    def __init__(self, db, data=None):
        self._db = db
        if isinstance(data, dict):
            self._data = data.copy()
            self._upgradeNote()
        elif data is not None:  # assume data is a key
            self.load(data)
        else:
            self._data = dict()
            self._upgradeNote()

    def _upgradeNote(self):
        if not self._data.has_key('key'):
            self._genKey()
        if not self._data.has_key('deleted'):
            self._data['deleted'] = 0
        if not self._data.has_key('createdate'):
            self._data['createdate'] = time.time()
        if not self._data.has_key('modifydate'):
            self._data['modifydate'] = time.time()
        if not self._data.has_key('content'):
            self._data['content'] = ''
        if not self._data.has_key('CHANGED'):
            self._data['CHANGED'] = True

    def getContent(self):
        return self._data['content'].decode('utf-8')

    def getTitle(self, length=20):
        content = self.getContent()
        eoln = content.find('\n')
        elipsis = ''
        if eoln < 0 or eoln > length:
            if eoln > length:
                elipsis = '...'
                eoln = length -3
            else:
                eoln = length
        return content[:eoln].replace('\r', ' ').replace('\t', ' ') + elipsis

    def setContent(self, text):
        self._data['content'] = text.rstrip()
        self._markModified()

    def getTags(self):
	if self._data.has_key('tags'):
	    return ' '.join(self._data['tags'])
	else:
	    return None

    def setTags(self, tags):
	'''tags should be list/tuple of strings, or space separated string
	'''
	from types import StringTypes
	if type(tags) in StringTypes:
	    tags = [ item.strip() for item in tags.split(' ') ]
	self._data['tags'] = list(tags)
	self._markModified()

    def _genKey(self):
        self._data['key'] = KEY_PREFIX + str(time.time())

    def _markModified(self):
        self._data['modifydate'] = time.time()
	self._data['CHANGED'] = True

    def _isModified(self):
	return self._data['CHANGED']

    def load(self, key):
        self._data = self._db.get(key)

    def save(self):
	self._db.update(self._data)

    def deleted(self):
        return self._data['deleted']

    def markDeleted(self):
        self._data['deleted'] = 1
        self._markModified()

    def getModifydate(self):
        return float(self._data['modifydate'])

    def getModifiedFormatted(self):
        sec = self.getModifydate()
        tsec = time.gmtime(sec)
        tnow = time.gmtime(time.time())
        if tsec[:3] == tnow[:3]:
            # today - return time only
            fmt = '%H:%M'
        elif tsec[:2] == tnow[:2]:
            # this month - return Month, Day
            fmt = '%b %d'
        else:
            fmt = '%Y-%m-%d'
        return time.strftime(fmt, time.localtime(sec))

    def getKey(self):
        return self._data['key']

if __name__ == '__main__':
    db = Database()
    for note in db.values():
	print note
	print '-' * 40
	
