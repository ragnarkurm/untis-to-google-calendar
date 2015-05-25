# -*- coding: utf-8 -*-

# this file has to be present in bin/

def basepath(*p):
	import os
	paths = map(lambda x: x, p) # tuple to list
	paths = ['..'] + paths
	paths = [os.path.dirname(__file__)] + paths
	paths = os.path.join(*paths)
	paths = os.path.abspath(paths)
	return paths

import sys
for p in ['lib', 'etc']:
	path = basepath(p)
	if not path in sys.path:
		sys.path.insert(1, path)
del path
del p
