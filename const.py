#!/usr/local/bin/python
#

from __future__ import print_function

import tree

class byte(tree.tree):
	def __init__(self, p, adr, len = 1, fmt="0x%02x"):
		tree.tree.__init__(self, adr, adr + len, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".BYTE\t"
		d = ""
		for i in range(t.start, t.end):
			x = p.m.rd(i)
			s += d
			s += self.fmt % x
			d = ", "
		return (s,)

class w16(tree.tree):
	def __init__(self, p, adr, len = 1, fmt="0x%04x"):
		tree.tree.__init__(self, adr, adr + len * 2, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".WORD\t"
		d = ""
		for i in range(t.start, t.end, 2):
			x = p.m.w16(i)
			s += d
			s += self.fmt % x
			d = ", "
		return (s,)

class txtlen(tree.tree):
	def __init__(self, p, adr, len):
		tree.tree.__init__(self, adr, adr + len, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.txt = p.m.ascii(adr, len)

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'" + self.txt + "'"
		return (s,)
