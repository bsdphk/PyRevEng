#!/usr/local/bin/python
#
 
from __future__ import print_function

import mem
 
class mem_domus(mem.base_mem):
	def __init__(self, start = 0, end = 0x10000):
		mem.base_mem.__init__(self, start, end, 16, 3, True)
		self.qchar= ("0", " ", "'", '"', 'x', 'y', 'z', '*')
		self.hex = False

	def dfmt(self, d, w = True):
		if self.hex and w:
			return "%04x" % d
		elif self.hex:
			return "%x" % d
		elif w:
			return "%06o" % d
		else:
			return "%o" % d

	def aqfmt(self, a, q):
		if self.hex:
			fmt = "%04x"
		else:
			fmt = "%06o"

		if q == 3:
			s = fmt % (a >> 1) + self.qchar[2] + "*2"
			if a & 1:
				s += "+1"
		else:
			s = fmt % a + self.qchar[q]
		return s

	def afmt(self, a):
		if a < 0x1000:
			return self.aqfmt(a, 1)
		elif a < 0x8000:
			return self.aqfmt(a, 2)
		else:
			return self.aqfmt(a, 7)

	def qfmt(self, q):
		return self.qchar[q]

	# adr/data/ascii column formatter
	# returns a list of lines, all the same width
	def col1(self, p, start, end, lvl):
		l = list()
		while start < end:
			try:
				x = self.rd(start)
				q = self.rdqual(start)
			except:
				l.append(self.afmt(start) + " --")
				start += 1
				continue
			s = self.afmt(start) + " " + self.dfmt(x)
			if self.qualifiers > 0:
				s += self.qfmt(q)
			s += "  |"
			for b in range(24,-1,-8):
				if self.bits > b:
					if q == 1:
						s += mem.ascii(x >> b)
					else:
						s += " "
			s += "|\t"
			l.append(s)
			start += 1
		return l

	# Default content formatter
	def col2(self, p, start, end, lvl):
		l = list()
		while start < end:
			q = p.m.rdqual(start)
			d = p.m.rd(start)
			s = ".XXX"
			if q == 3:
				s += "\t" + self.aqfmt(d, q)
			l.append(s)
			start += 1
		return l

