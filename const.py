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

class ptr(tree.tree):
	def __init__(self, p, adr, width = 2, len = 1):
		tree.tree.__init__(self, adr, adr + len * width, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.width = width

	def rfunc(self, p, t):
		s = ".PTR\t"
		d = ""
		for i in range(t.start, t.end, self.width):
			if self.width == 2:
				x = p.m.w16(i)
			elif self.width == 4:
				x = p.m.w32(i)
			else:
				assert self.width == "Wrong width"
			s += d
			if x in p.label:
				s += p.label[x]
			else:
				s += p.m.afmt(x)
			d = ", "
		return (s,)

class ltxt(tree.tree):
	def __init__(self, p, adr, align=2):
		l = p.m.rd(adr)
		len = l + 1
		len += align - 1
		len &= ~(align -1)
		tree.tree.__init__(self, adr, adr + len, "const")
		p.t.add(self.start, self.end, self.tag, True, self)

		self.render = self.rfunc
		self.l = l
		self.txt = p.m.ascii(adr + 1, l)

	def rfunc(self, p, t):
		s = ".LTXT\t%d,'" % self.l + self.txt + "'"
		return (s,)

class txtlen(tree.tree):
	def __init__(self, p, adr, len, align=1):
		llen = len + align - 1
		llen &= ~(align -1)
		tree.tree.__init__(self, adr, adr + llen, "const")
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

class fill(tree.tree):
	def __init__(self, p, lo = None, mid = None, hi = None, fmt = None, rd = None):
		if rd == None:
			rd = p.m.rd
		if fmt == None:
			fmt = p.m.dpct
		if lo == None:
			if mid != None:
				lo = mid
			elif hi != None:
				lo = hi
			else:
				print("BOGUS fill(", lo, ",", mid, ",", hi, ")")
				return
			x = rd(lo)
			while x == rd(lo - 1):
				lo -= 1
		if hi == None:
			if mid != None:
				hi = mid
			elif lo != None:
				hi = lo
			else:
				print("BOGUS fill(", lo, ",", mid, ",", hi, ")")
				return
			x = rd(hi)
			try:
				while x == rd(hi):
					hi += 1
				hi -= 1
			except:
				pass
		if lo == None or hi == None:
			print("BOGUS fill(", lo, ",", mid, ",", hi, ")")
			return
		hi += 1
		tree.tree.__init__(self, lo, hi, "fill")
		x = p.t.add(self.start, self.end, self.tag, True, self)
		x.render = ".Fill\t" + \
		    fmt % rd(lo) + "[" + fmt % (hi-lo) + "]"
		x.fold = True

def seven_seg_lcmt(y, val, map = ( 1, 2, 4, 8, 16, 32, 64, 128, 0)):
	if val & map[0]:
		y.lcmt("  --")
	else:
		y.lcmt("    ")

	if val & map[5]:
		s = " |"
	else:
		s = "  "
	if val & map[1]:
		y.lcmt(s + "  |")
	else:
		y.lcmt(s + "   ")

	if val & map[6]:
		y.lcmt("  --")
	else:
		y.lcmt("    ")

	if val & map[4]:
		s = " |"
	else:
		s = "  "
	if val & map[2]:
		y.lcmt(s + "  |")
	else:
		y.lcmt(s + "   ")

	if val & map[8]:
		s = "."
	else:
		s = " "
	if val & map[3]:
		s += " -- "
	else:
		s += "    "
	if val & map[7]:
		y.lcmt(s + ".")
	else:
		y.lcmt(s)
	y.lcmt(" ")

class seven_segment(tree.tree):
	def __init__(self, p, adr,
	    map = ( 1, 2, 4, 8, 16, 32, 64, 128, 0)):
		tree.tree.__init__(self, adr, adr + 1, "7seg")
		y = p.t.add(self.start, self.end, self.tag, True, self)
		val = p.m.rd(adr)
		y.render = ".BYTE 0x%02x" % val
		seven_seg_lcmt(y, val, map)
