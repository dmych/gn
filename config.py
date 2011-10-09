# simple config file

class Config(object):
    '''Simple config file with line format var=val
    '''
    def __init__(self, filename):
	self.data = dict()
	self.order = list()
	self.fname = filename
	self._read_data()

    def __getitem__(self, key):
	return self.data[key]

    def __setitem__(self, key, value):
	self.data[key] = value
	if key not in self.order:
	    self.order.append(key)

    def has_key(self, key):
	return self.data.has_key(key)

    def _read_data(self):
	try:
	    fd = open(self.fname, 'r')
	except:
	    raise Exception('Cannot find file %s' % self.fname)
	for line in fd.readlines():
	    line = line.strip()
	    if not line or line.startswith('#'):
		continue
	    try:
		k, v = line.strip().split('=')
	    except ValueError:
		raise Exception('Invalid line in config file %s:\n%s' % (self.fname, line))
	    self.data[k] = v
	    if k not in self.order:
		self.order.append(k)
	fd.close()

    def save(self):
	try:
	    fd = open(self.fname, 'w')
	except:
	    raise Exception('Cannot write to %s' % self.fname)
	for key in self.order:
	    fd.write('%s=%s\n' % (key, self.data[key]))
	fd.close()

    def __del__(self):
	self.save()
	
		     
