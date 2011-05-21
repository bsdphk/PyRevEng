#!/usr/local/bin/python
#
 
from __future__ import print_function

import mem
 
class mem_domus(mem.base_mem):
	def __init__(self, start = 0, end = 0x10000):
		mem.base_mem.__init__(self, start, end, 16, 3, True)
		self.qchar= ("0", " ", "'", '"', 'a', 'b', 'c', '*')
		self.dpct = "%06o"

	def afmt(self, a):
		if a < 0x1000:
			return "%06o " % a
		elif a < 0x8000:
			return "%06o'" % a
		else:
			return "%06o*" % a

	def qfmt(self, q):
		return self.qchar[q]
