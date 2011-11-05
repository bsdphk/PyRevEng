#!/usr/local/bin/python
#
# This is the class that simulates memory.
#
# In addition to a word-size, it is possible to store "qualifier" bits
# with each word.  This can be used to mark memory words with bits of
# various observations, one example being "relocated" which usually
# is a strong indication of non-instruction-ness
#

from __future__ import print_function

import struct
import array

def ascii(x):
	x &= 0xff
	if x < 32 or x > 126:
		return " "
	return "%c" % x


#######################################################################
#
# We report trouble as these exceptions
#

class MemError(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)

#######################################################################
#
# A very abstract memory class, can handle up to 32 bit wide locations,
# including (optional) flags and qualifiers
#

class base_mem(object):
	def __init__(self, start=0, end=0, bits=8, qualifiers=0, flags=False):
	
		if end < start:
			raise MemError(start,
			    "Negative Length (0x%x-0x%x" % (start, end))

		self.start = start
		self.end = end
		self.flags = flags
		self.qualifiers = qualifiers
		self.bits = bits

		self.qmask = ((1<<qualifiers) - 1) << bits
		self.bmask = (1<<bits) - 1

		self.apct = "%%0%dx" % len("%x" % (self.end - 1))
		self.dpct = "%%0%dx" % (bits / 4)
		self.qpct = "[%%0%dx]" % (qualifiers / 4)

		w = bits + qualifiers
		if flags:
			self.fmask = ((1<<6) - 1) << w
			# Flag bits
			self.can_read =		1 << (w + 0)
			self.can_write =	1 << (w + 1)
			self.invalid =		1 << (w + 2)
			self.undef =		1 << (w + 3)
			self.acc_read =		1 << (w + 4)
			self.acc_write =	1 << (w + 5)
			w += 6
		else:
			self.can_read =		0
			self.can_write =	0
			self.invalid =		0
			self.undef =		0
			self.acc_read =		0
			self.acc_write =	0
		if w <= 8:
			self.mem = array.array('B')
		elif w <= 16:
			self.mem = array.array('H')
		elif w <= 32:
			self.mem = array.array('L')
		else:
			raise MemError(w, "Too many bits (%d) wide" % w)
		for a in range(self.start, self.end):
			self.mem.append(self.invalid | self.undef)

	# Format a memory address as a hex string
	# If you don't like hex, you can override .[adq]pct or subclass
	# and overload .[adq]fmt()

	def afmt(self, a):
		return self.apct % a

	def dfmt(self, d):
		return self.dpct % d

	def qfmt(self, q):
		return self.qpct % q

	# Default adr/data/ascii column formatter
	# returns a list of lines, all the same width
	def col1(self, p, start, end, lvl):
		l = list()
		while start < end:
			try:
				x = self.rd(start)
			except:
				l.append(self.afmt(start) + " --")
				start += 1
				continue
			s = self.afmt(start) + " " + self.dfmt(x)
			if self.qualifiers > 0:
				s += self.qfmt(self.rdqual(start))
			s += "  |"
			for b in range(24,-1,-8):
				if self.bits > b:
					s += ascii(x >> b)
			s += "|\t"
			l.append(s)
			start += 1
		return l

	# Default content formatter
	def col2(self, p, start, end, lvl):
		l = list()
		while start < end:
			l.append(".XXX")
			start += 1
		return l

	# Check if an address is inside this piece of memory
	def chkadr(self, start, end=None):
		if start < self.start:
			raise MemError(start, "Invalid location")
		if start > self.end:
			raise MemError(start, "Invalid location")
		if end == None:
			return
		if end < self.start:
			raise MemError(end, "Invalid location")
		if end > self.end:
			raise MemError(end, "Invalid location")

	# Set some flags on a range of memory
	def setflags(self, start, end = None, set=0, reset=0):
		if not self.flags:
			return
		if set & ~self.fmask:
			raise MemError(start,
			    "Invalid set flag (0x%x)" % set)
		if reset & ~self.fmask:
			raise MemError(start,
			    "Invalid reset flag (0x%x)" % reset)
		self.chkadr(start, end)
		if end == None:
			end = start + 1
		for i in range(start, end):
			self.mem[i - self.start] |= set
			self.mem[i - self.start] &= ~reset

	# Test if flags are set on all locations in range
	def tstflags(self, start, end = None, flags = 0, fallback=None):
		if not self.flags:
			return fallback
		if flags & ~self.fmask:
			raise MemError(start,
			    "Invalid set flag (0x%x)" % flags)
		self.chkadr(start, end)
		if end == None:
			end = start + 1
		for i in range(start, end):
			if not self.mem[i - self.start] & flags:
				return False
		return True

	# Read a single location
	def rd(self, adr):
		assert type(adr) == int
		self.chkadr(adr)
		x = self.mem[adr - self.start]
		if self.flags:
			if x & self.invalid:
				raise MemError(adr, "Invalid location")
			if not x & self.can_read:
				raise MemError(adr, "Read forbidden")
			self.mem[adr - self.start] |= self.acc_read
			if x & self.undef:
				return None
		return x & self.bmask

	# Write a single location
	def wr(self, adr, data):
		self.chkadr(adr)
		i = adr - self.start
		if data & ~self.bmask:
			raise MemError(adr,
			    "Write illegal bits (0x%x)" % data)
		x = self.mem[i]
		if self.flags:
			if x & self.invalid:
				raise MemError(adr, "Invalid location")
			if not x & self.can_write:
				raise MemError(adr, "Write forbidden")
			x |= self.acc_write
			x &= ~self.undef
		self.mem[i] = (x & ~self.bmask) | data

	# Read a single location
	def rdqual(self, adr):
		assert type(adr) == int
		self.chkadr(adr)
		x = self.mem[adr - self.start]
		if self.flags:
			if x & self.invalid:
				raise MemError(adr, "Invalid location")
			if not x & self.can_read:
				raise MemError(adr, "Read forbidden")
			if x & self.undef:
				return None
		return (x & self.qmask) >> self.bits

	# Write a single location
	def wrqual(self, adr, qual):
		self.chkadr(adr)
		i = adr - self.start
		if (qual << self.bits) & ~self.qmask:
			raise MemError(adr,
			    "Write illegal qualifier (0x%x)" % qual)
		x = self.mem[i]
		if self.flags:
			if x & self.invalid:
				raise MemError(adr, "Invalid location")
			if not x & self.can_write:
				raise MemError(adr, "Write forbidden")
		self.mem[i] = (x & ~self.qmask) | (qual << self.bits)

	# Find a particular pattern
	# 'None' is a wildcard
	def find(self, start, end, pattern):
		l = list()
		lx = len(pattern)
		i = 0
		for ax in range(start, end-lx):
			if pattern[i] != None:
				try:
					x = self.rd(ax)
				except:
					i = 0
					continue
				if pattern[i] != x:
					i = 0
					continue
			i += 1
			if i < lx:
				continue
			l.append(ax - (lx-1))
			i = 0
		return l

#######################################################################
#
# The normal microprocessor byte addressable model
#

class byte_mem(base_mem):
	def __init__(self, start=0, end=0, qualifiers=0, flags=False, endian=None):
		base_mem.__init__(self,
		    start = start,
		    end = end,
		    bits = 8,
		    qualifiers = qualifiers,
		    flags = flags)
		# Number of bytes per line
		self.bcols = 8
		if endian == "big-endian" or endian == ">":
			self.w16 = self.b16
			self.s16 = self.sb16
			self.w32 = self.b32
			self.s32 = self.sb32
		elif endian == "little-endian" or endian == "<":
			self.w16 = self.l16
			self.s16 = self.sl16
			self.w32 = self.l32
			self.s32 = self.sl32
		elif endian != None:
			raise MemError(0, "Unknown endianess (%s)" % endian)

	# All these functions come in big and little endian
	# signed versions have 's' prefix
	def s8(self, adr):
		a = self.rd(adr)
		if a & 0x80:
			a -= 256
		return a

	def l16(self, adr):
		return self.rd(adr + 1) << 8 | self.rd(adr)
	def b16(self, adr):
		return self.rd(adr) << 8 | self.rd(adr + 1)
	def sl16(self, adr):
		a = self.l16(adr)
		if a & 0x8000:
			a -= 65536
		return a
	def sb16(self, adr):
		a = self.b16(adr)
		if a & 0x8000:
			a -= 65536
		return a

	def l32(self, adr):
		return self.rd(adr + 3) << 24 | \
		    self.rd(adr + 2) << 16 | \
		    self.rd(adr + 1) << 8 | self.rd(adr)

	def sl32(self, adr):
		v = self.l32(adr)
		if v & (1 << 31):
			return v - (1<<32)
		return v

	def b32(self, adr):
		return self.rd(adr) << 24 | \
		    self.rd(adr + 1) << 16 | \
		    self.rd(adr + 2) << 8 | self.rd(adr + 3)

	def sb32(self, adr):
		v = self.b32(adr)
		if v & (1 << 31):
			return v - (1<<32)
		return v

	def ascii(self, adr, len=-1):
		s = ""
		while True:
			x = self.rd(adr)
			if len == -1 and x == 0:
				break
			if x >= 32 and x <= 126:
				s += "%c" % x
			elif x == 10:
				s += "\\n"
			elif x == 13:
				s += "\\r"
			else:
				s += "\\x%02x" % x
			if len > 0:
				len -= 1
				if len == 0:
					break
			adr += 1
		return s

	def fromfile(self, fn, offset = 0, step = 1):
		f = open(fn, "rb")
		d = f.read()
		d = bytearray(d)
		f.close()
		for i in d:
			self.setflags(offset, None,
			    self.can_read|self.can_write,
			    self.invalid|self.undef)
			self.wr(offset, i)
			offset += step

	def col1(self, p, start, end, lvl):
		l = list()
		while start < end:
			s = self.afmt(start)
			s += " "
			t = "|"
			for i in range(0,self.bcols):
				if start + i >= end:
					s += "   "
					t += " "
				else:
					try:
						x = self.rd(start + i)
					except:
						s += " --"
						t += " "
						continue

					s += " %02x" % x
					t += ascii(x)
			s += "  " + t + "| "
			s += p.indent
			l.append(s)
			start += self.bcols
		return l

	# Default content formatter
	def col2(self, p, start, end, lvl):
		l = list()
		while start < end:
			l.append(".XXX")
			start += self.bcols
		return l

class seg_mem(object):
	def __init__(self, segmask, offmask):
		assert (segmask & offmask) == 0

		self.segmask = segmask
		self.segshift = 0
		while not (segmask & (1 << self.segshift)):
			self.segshift += 1

		self.offmask = offmask
		self.offshift = 0
		while not (offmask & (1 << self.offshift)):
			self.offshift += 1

		self.nonmask = ~(segmask | offmask)

		print("SEGmem(%08x, %d, %08x, %d, %08x)" % (
		    self.segmask, self.segshift,
		    self.offmask, self.offshift,
		    self.nonmask
		))

		self.segs = dict()
		self.start= None
		self.end= None

		self.segfmt = "%02x:"

	def seg_off(self, adr):
		if adr & self.nonmask:
			raise MemError(start,
			    "Invalid segmented address 0x%x" % adr)
		s = (adr & self.segmask) >> self.segshift
		o = (adr & self.offmask) >> self.offshift
		return (s,o)

	def linadr(self, seg, off):
		return (seg << self.segshift) | (off << self.offshift)


	def next_adr(self, adr):
		s = (adr & self.segmask) >> self.segshift
		o = (adr & self.offmask) >> self.offshift
		if s in self.segs:
			try:
				r = self.segs[s].next_adr(o)
				return r
			except:
				pass
		s += 1
		return (s << self.segshift)


	def afmt(self, adr):
		s,o = self.seg_off(adr)
		return self.segfmt % s + self.segs[s].afmt(o)
	

	def add_seg(self, seg, m):
		assert seg not in self.segs
		assert m.end - 1 <= self.offmask
		b = seg << self.segshift
		if self.start == None or b < self.start:
			self.start = b
		if self.end == None or b > self.end:
			self.end = b + m.end
		self.segs[seg] = m

	def rd(self, adr):
		s,o = self.seg_off(adr)
		return self.segs[s].rd(o)

	def w16(self, adr):
		s,o = self.seg_off(adr)
		return self.segs[s].w16(o)

	def b16(self, adr):
		s,o = self.seg_off(adr)
		return self.segs[s].b16(o)

	def b32(self, adr):
		s,o = self.seg_off(adr)
		return self.segs[s].b32(o)

	def w32(self, adr):
		s,o = self.seg_off(adr)
		return self.segs[s].w32(o)

	def chkadr(self, adr):
		try:
			s,o = self.seg_off(adr)
		except:
			raise MemError(start, "Invalid location")
		if not s in self.segs:
			raise MemError(start, "Invalid location")
		return self.segs[s].chkadr(o)

	def ascii(self, adr, len):
		s,o = self.seg_off(adr)
		return self.segs[s].ascii(o, len)

	def col1(self, p, start, end, lvl):
		ss,so = self.seg_off(start)
		es,eo = self.seg_off(end)
		assert ss == es
		c1 = self.segs[ss].col1(p, so, eo, lvl)
		c11 = list()
		for i in c1:
			c11.append(self.segfmt % ss + i)
		return c11

	def col2(self, p, start, end, lvl):
		ss,so = self.seg_off(start)
		es,eo = self.seg_off(end)
		assert ss == es
		return self.segs[ss].col2(p, so, eo, lvl)

if __name__ == "__main__":

	m = byte_mem(0,0x500)
