#!/usr/local/bin/python
#
# Try to recognize which CODEPROCEDURES have been linked into a program
# by matching against preloaded domus libraries.  We built a dictionary 
# tree of position independent information and  walk that.

from __future__ import print_function

import mem_domus
import file_domus

def sign(m, off, adr):
	q = m.rdqual(adr)
	d = m.rd(adr)
	if q == 2:
		d -= off
	if q == 3:
		d -= 2 * off
	return "%04x%d," % (d, q)

class domus_libs(object):
	def __init__(self, prefix = None, filenames = None):
		if prefix == None:
			prefix = "/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/__."
		if filenames == None:
			filenames = list()
			filenames.append("CODEP")
			filenames.append("CODEX")
			filenames.append("ULIB")
			filenames.append("FSLIB")
		self.t = dict()
		self.filenames = filenames
		self.prefix = prefix
		self.loaded = False
	

	def load(self, prefix, filename):
		f = file_domus.file_domus(prefix + filename)
		for obj in f.build_index():
			m = mem_domus.mem_domus()
			f.load(m, obj, silent=True)
			ln = 1 + f.max_nrel - f.min_nrel
			lz = 1 + f.max_zrel - f.min_zrel
			assert lz == 0
			t = self.t
			for i in range(f.min_nrel, f.max_nrel + 1):
				s = sign(m, f.min_nrel, i)
				if not s in t:
					t[s] = dict()
				t = t[s]
			if not 'Z' in t:
				t['Z'] = list()
			t['Z'].append(filename + "::" + obj)

	def match(self, tmem, tadr):
		if not self.loaded:
			for fn in self.filenames:
				self.load(self.prefix, fn)
			self.loaded = True
		t = self.t
		adr = tadr
		while True:
			s = sign(tmem, tadr, adr)
			if not s in t:
				return None
			t = t[s]
			if 'Z' in t:
				return (tadr, adr, t['Z'])
			adr += 1
			

if __name__ == "__main__":
	dl = domus_libs()
