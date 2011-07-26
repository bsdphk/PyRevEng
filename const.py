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

	def rfunc(self, p, t):
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

	def rfunc(self, p, t):
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

	def rfunc(self, p, t):
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

	def rfunc(self, p, t):
		s = ".TXT\t'" + self.txt + "'"
		return (s,)

class txt(tree.tree):
	def __init__(self, p, adr, len = None, descend=True):
		elen = 0
		self.term=""
		if len == None:
			len = 0;
			while True:
				c = p.m.rd(adr + len)
				if c == 0x00:
					self.term=",0"
					elen = 1
					break;
				len += 1
				if c != 0x0a:
					continue
				# We treat newlines special:
				# If it looks like text continues
				# start another instance on the next line
				# XXX: means length don't match, bad!
				c2 = p.m.rd(adr + len)
				if c2 == 0x0a or c2 == 0x00:
					continue
				txt(p, adr + len, descend=descend)
				break;
		if len <= 0:
			print("BOGUS const.txt @%x" % adr)
			return
		tree.tree.__init__(self, adr, adr + len + elen, "const")
		x = p.t.add(self.start, self.end, self.tag, True, self)
		x.descend = descend

		self.render = self.rfunc
		if len > 0:
			self.txt = p.m.ascii(adr, len)
		else:
			self.txt = ""

	def rfunc(self, p, t):
		s = ".TXT\t'" + self.txt + "'" + self.term
		return (s,)
