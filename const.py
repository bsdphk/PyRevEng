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

class w32(tree.tree):
	def __init__(self, p, adr, len = 1, fmt="0x%08x"):
		tree.tree.__init__(self, adr, adr + len * 4, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".LWORD\t"
		d = ""
		for i in range(t.start, t.end, 4):
			x = p.m.w32(i)
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

class txt(tree.tree):
	def __init__(self, p, adr, len = None):
		if len == None:
			len = 0;
			while p.m.rd(adr + len) != 0:
				len += 1
			flen = len
			len += 1
		else:
			flen = len
		if len <= 0:
			print("BOGUS const.txt @%x" % adr)
			exit(0)
			return
		tree.tree.__init__(self, adr, adr + len, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		if flen > 0:
			self.txt = p.m.ascii(adr, flen)
		else:
			self.txt = ""

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'" + self.txt + "'"
		return (s,)
