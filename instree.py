#!/usr/local/bin/python
#

from __future__ import print_function

#######################################################################
# Parse a "([01x] )*[01x]" string into a mask + bits

def parse_match(bit, f):
	mask = 0
	bits = 0
	width = 0
	l = len(f)
	if l & 1 == 0:
		return None
	i = 0
	while i < l:
		mask <<= 1
		bits <<= 1
		width += 1
		if f[i] == "0":
			mask |= 1
		elif f[i] == "1":
			mask |= 1
			bits |= 1
		elif f[i] == "x":
			pass
		else:
			return None
		i += 1
		if i < l and f[i] != " ":
			return None
		i += 1
	return (bit, width, mask, bits)

#######################################################################
# A single line from the specification

class insline(object):
	def __init__(self, line, width = 8, endian = "big"):
		#print("\n" + line)
		s = line.expandtabs().split("|")
		self.spec = s[0].split()
		b = 0
		l1 = list()
		l2 = list()
		for i in s[1:]:
			if i == "":
				continue
			f = parse_match(b, i)
			if f != None:
				l1.append(f)
			else:
				if len(i) & 1 == 0:
					print(
					    "Error: Field has half bit:\n" +
					    "  %s\n" % line,
					    "  '%s'" % i)
					assert False
				w = (len(i) + 1) >> 1
				f = (b, w, i.strip())
				l2.append(f)
			b += f[1]

		if b % width != 0:
			print(
			    ("Error: %d not an multiple of %d bits.\n" +
			    "  %s") % (b, width, line))
			assert False

		self.width = b
		self.mask = list()
		self.bits = list()
		for i in range(0, int(b/width)):
			self.mask.append(0)
			self.bits.append(0)

		for i in l1:
			s = i[1] - 1
			for b in range(i[0], i[0] + i[1]):
				j = int(b / width)
				r = b % width + 1
				assert endian == "big"
				if i[2] & (1 << s):
					self.mask[j] |= 1 << (width - r)
				if i[3] & (1 << s):
					self.bits[j] |= 1 << (width - r)
				s -= 1
			assert s == -1
		self.fld = l2

	def __repr__(self):
		s = "w%d <" % self.width
		t = ""
		for i in self.spec:
			s += t + i
			t = " "
		s += "> <"
		t = ""
		for i in range(0, len(self.mask)):
			s += t + "%02x|%02x" % (self.mask[i], self.bits[i])
			t = ","
		s += "> <"
		t = ""
		for i in self.fld:
			s += t + i[2]
			t = ","
		s += ">"
		return s

#######################################################################
# 

class insbranch(object):
	def __init__(self, lvl):
		self.lvl = lvl
		self.spec = list()

	def insert(self, x):
		#print(">>", x)
		m = x.mask[self.lvl]
		b = x.bits[self.lvl]
		for i in self.spec:
			if m != i[0]:
				continue
			if b in i[1]:
				if type(i[1][b]) == insbranch:
					i[1][b].insert(x)
					return
				y = insbranch(self.lvl + 1)
				y.insert(i[1][b])
				y.insert(x)
				i[1][b] = y
				return
			i[1][b] = x
			return
		l = list()
		l.append(m)
		l.append(dict())
		l[1][b] = x
		for j in range(0, len(self.spec)):
			i = self.spec[j]
			if ~(m & i[0]) & m:
				self.spec.insert(j, l)
				return
		self.spec.append(l)

	def __repr__(self):
		return "<Branch %d>" % self.lvl

	def print(self):
		f = ""
		for i in range(0, self.lvl):
			f += "    "
		for i in self.spec:
			print(f + "  & %02x" % i[0])
			for j in i[1]:
				if type(i[1][j]) == insbranch:
					print(f + "    %02x" % j)
					i[1][j].print()
				else:
					print(f + "    %02x" % j, i[1][j])

	def find(self, v):
		for i in self.spec:
			b = v & i[0]
			if b in i[1]:
				return i[1][b]
		return None

#######################################################################
# 

class instree(object):
	def __init__(self, width=8, endian="big"):
		self.width = width
		self.endian = endian
		self.ins = list()
		self.root = insbranch(0)

	def load(self, filename):
		fi = open(filename, "r")
		for i in fi.readlines():
			i = i.strip()
			if i == "" or i[0] == "#":
				continue
			x = insline(i, self.width, self.endian)
			self.ins.append(x)
			self.root.insert(x)
		fi.close()

	def print(self):
		self.root.print()

	def find(self, p, adr, func, incr = None):
		if incr == None:
			incr = self.width >> 3
		r = self.root
		for i in range(0,10, incr):
			b = func(adr + i)
			x = r.find(b)
			if type(x) != insbranch:
				return x
		return None
