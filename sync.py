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
sync.py: synchronization between local database and remote service
'''

from api import Simplenote
from db import Database, KEY_PREFIX
import time
import sys

VERBOSE_DEBUG = False

def dbg(msg):
    if not VERBOSE_DEBUG: return
    from sys import stderr
    stderr.write('**** %s\n' % (msg))

def sync(user, password, since=None, localdb=None):
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
    if since:
	rindex = api.index(since=since)
	dbg('>>>> SINCE: %s' % since)
    else:
	rindex = api.index()
    dbg('REMOTE TO LOCAL:')
    dbg('>>>> RINDEX LEN: %s' % len(rindex))
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
    if since is None:
	rkeys = api.keys().keys()
	for k in db.keys(deleted=True):
	    if k not in rkeys:
		dbg('  DEL: %s' % k)
		db.remove(k)
		synced_count += 1
    else:
	for k in db.keys(deleted=True):
	    litem = db.get(k)
	    if litem['deleted'] != 0:
		dbg('  DEL: %s' % k)
		db.remove(k)
    sys.stderr.write('Synced %s notes.\n' % synced_count)
    return time.time()
	    
if __name__ == '__main__':
    import sys
    email = sys.argv[1]
    password = sys.argv[2]
    sync(email, password)
