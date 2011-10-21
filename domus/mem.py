#!/usr/local/bin/python
#
 
from __future__ import print_function

import mem
 
class mem_domus(mem.base_mem):
	def __init__(self, start = 0, end = 0x10000):
		mem.base_mem.__init__(self, start, end, 16, 3, True)
		self.qchar= ("0", " ", "'", '"', 'a', 'b', 'c', '*')
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

	def afmt(self, a):
		if self.hex:
			if a < 0x1000:
				return "%04x " % a
			elif a < 0x8000:
				return "%04x'" % a
			else:
				return "%04x*" % a
		else:
			if a < 0x1000:
				return "%06o " % a
			elif a < 0x8000:
				return "%06o'" % a
			else:
				return "%06o*" % a

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
				s += "\t%o'*2" % (d >> 1)
				if d & 1:
					s += "+1"
			l.append(s)
			start += 1
		return l

