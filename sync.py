# sync.py: synchronization between local database and remote service

'''This is a part of simpla project
Simpla is a simplenote portableclient written in Python
Copyright (c) Dmitri Brechalov, 2010
'''

from api import Simplenote
from db import Database, KEY_PREFIX

VERBOSE_DEBUG = False

def dbg(msg):
    if not VERBOSE_DEBUG: return
    from sys import stderr
    stderr.write('**** %s\n' % (msg))

def sync(user, password, localdb=None):
    db = Database(localdb)
    api = Simplenote(user, password)
    dbg('LOCAL TO REMOTE:')
    synced_count = 0
    for note in db.values():
	if note['CHANGED']:
	    if not note.has_key('key') or note['key'].startswith(KEY_PREFIX):
		dbg('NEW NOTE')
	    else:
		dbg('CHANGED: %s' % note['key'])
	    if note['key'].startswith(KEY_PREFIX):
		k = note['key']
		del note['key']
	    else:
		k = None
	    note = api.update(note)
	    note['CHANGED'] = False
	    db.update(note)
	    if k is not None:
		db.remove(k)
	    synced_count += 1
    rindex = api.index()
    dbg('REMOTE TO LOCAL:')
    for ritem in rindex:
	key = ritem['key']
	if key not in db.keys(deleted=True):
	    dbg('  NEW: %s' % (key))
	    db.update(api.get(key))
	    synced_count += 1
	litem = db.get(key)
	if ritem['syncnum'] > litem['syncnum']:
	    dbg('  UPD: %s' % (key))
	    db.update(api.get(key))
	    synced_count += 1
    dbg('CLEAN UP:')
    rkeys = api.keys().keys()
    for k in db.keys(deleted=True):
	if k not in rkeys:
	    dbg('  DEL: %s' % k)
	    db.remove(k)
	    synced_count += 1
    print 'Synced', synced_count, 'notes.'
	    
if __name__ == '__main__':
    import sys
    email = sys.argv[1]
    password = sys.argv[2]
    sync(email, password)
