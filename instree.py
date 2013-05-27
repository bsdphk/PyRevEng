#!/usr/local/bin/python
#

from __future__ import print_function

from disass import DisassError

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
	def __init__(self, line, width = 8):
		self.mask = list()
		self.bits = list()
		self.flds = dict()

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
		for i in range(0, int(b/width)):
			self.mask.append(0)
			self.bits.append(0)

		# Convert match fields to mask/bits
		# XXX: there must be a cleaner way...
		for i in l1:
			s = i[1] - 1
			for b in range(i[0], i[0] + i[1]):
				j = int(b / width)
				r = b % width + 1
				if i[2] & (1 << s):
					self.mask[j] |= 1 << (width - r)
				if i[3] & (1 << s):
					self.bits[j] |= 1 << (width - r)
				s -= 1
			assert s == -1

		#print(line)
		for i in l2:
			b = i[0]
			w = i[1]
			e = b + w - 1
			if int(b / width) != int(e / width):
				print(
				    "Error: Field %s spans " % i[2] +
				    "%d-bit units:\n" % self.width +
				    "  %s\n" % line)
				assert False
			s = int(b / width)
			b -= s * width
			e -= s * width
			m = (1<<w) - 1
			#print(i[2], width - (1 + e), "0x%x" % m)
			self.flds[i[2]]= (s, width - (1 + e), m)
		self.line = line

	def get_field(self, p, adr, func, scale, name):
		if name not in self.flds:
			return None
		x = self.flds[name]
		v = (func(adr + x[0] * scale) >> x[1]) & x[2]
		#print(p, adr, func, name, x, "\n", self.line, "0x%x" % v)
		return v


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
			t = ", "
		s += "> <"
		t = ""
		for i in self.flds:
			s += t + i
			t = ", "
		s += ">"
		return s

#######################################################################
#  Branch-point

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
				if len(x.mask) > self.lvl + 1 or \
				   len(i[1][b].mask) > self.lvl + 1:
					y = insbranch(self.lvl + 1)
					y.insert(i[1][b])
					y.insert(x)
					i[1][b] = y
					return
				else:
					print("Error:  Collision")
					print(x)
					print(i[1][b])
					assert False
			if self.lvl + 1 == len(x.mask):
				i[1][b] = x
			else:
				y = insbranch(self.lvl + 1)
				y.insert(x)
				i[1][b] = y
			return
		l = list()
		l.append(m)
		l.append(dict())
		if self.lvl + 1 == len(x.mask):
			l[1][b] = x
		else:
			y = insbranch(self.lvl + 1)
			y.insert(x)
			l[1][b] = y
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
			print(f + "  & %04x" % i[0])
			for j in sorted(i[1].keys()):
				if type(i[1][j]) == insbranch:
					print(f + "    %04x" % j)
					i[1][j].print()
				else:
					print(f + "    %04x " % j, i[1][j])

	def find(self, v):
		for i in self.spec:
			b = v & i[0]
			if b in i[1]:
				return i[1][b]
		return None

	def addone(self, l, y):
		# Only add if the new entry is not a proper subset of
		# of an already existing entry.
		for j in l:
			x = False
			for k in range(0, len(j.mask)):
				if k >= len(y.mask):
					break
				if y.mask[k] & j.mask[k] != y.mask[k]:
					x = True
			if not x:
				return
		l.append(y)

	def allfind(self, adr, func, incr, l):
		v = func(adr)
		for i in self.spec:
			b = v & i[0]
			if not b in i[1]:
				continue
			y = i[1][b]
			if type(y) == insbranch:
				y.allfind(adr + incr, func, incr, l)
			else:
				self.addone(l, y)
		return l

#######################################################################
# 

class instree(object):
	def __init__(self, width=8, filename=None):
		self.width = width
		self.root = insbranch(0)
		if filename != None:
			self.load(filename)

	def load(self, filename):
		fi = open(filename, "r")
		for i in fi.readlines():
			i = i.strip()
			if i == "" or i[0] == "#":
				continue
			x = insline(i, self.width)
			self.root.insert(x)
		fi.close()

	def load_string(self, s):
		for i in s.split("\n"):
			i = i.strip()
			if i == "" or i[0] == "#":
				continue
			x = insline(i, self.width)
			self.root.insert(x)

	def print(self):
		self.root.print()

	def find(self, p, adr, func, incr = None):
		if incr == None:
			incr = self.width >> 3
		r = self.root
		for i in range(0,10, incr):
			b = func(adr + i)
			r = r.find(b)
			if type(r) != insbranch:
				break
		if r == None:
			raise DisassError("no matching ins")
		return r

	# This finds all non-overlapping candidates.
	# such as mask=0xf002 and mask=0xf001
	# but not mask=0xf001 and mask=0xf000
	def allfind(self, p, adr, func, incr = None):
		l = list()
		if incr == None:
			incr = self.width >> 3
		self.root.allfind(adr, func, incr, l)
		return l

if __name__ == "__main__":
	it = instree(8, "cpus/mcs51_instructions.txt")
	it.print()
