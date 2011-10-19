#!/usr/local/bin/python
#

class bitmap(object):
	def __init__(self, low = 0, high = None):
		assert type(low) == int
		self.low = low
		self.high = high
		assert high == None or type(high) == int
		if self.high == None:
			self.mem = bytearray()
		else:
			assert high > low
			w = ((high - low) | 7) + 1
			self.mem = bytearray(w >> 3)

	def set(self, n):
		assert type(n) == int
		assert n >= self.low
		n -= self.low
		if self.high != None:
			assert n <= self.high
		b = n >> 3
		i = 0x80 >> (n & 7)

		if self.high == None and len(self.mem) <= b:
			self.mem += bytearray(b + 1 - len(self.mem))
		self.mem[b] |= i
	
	def mset(self, lo, hi):
		for i in range(lo, hi):
			self.set(i)

	def clr(self, n):
		assert type(n) == int
		assert n >= self.low
		n -= self.low
		if self.high != None:
			assert n <= self.high
		b = n >> 3
		i = 0x80 >> (n & 7)

		if self.high == None and len(self.mem) <= b:
			self.mem += bytearray(b + 1 - len(self.mem))
		self.mem[b] &= ~i

	def mclr(self, lo, hi):
		for i in range(lo, hi):
			self.clr(i)

	def tst(self, n):
		assert type(n) == int
		assert n >= self.low
		n -= self.low
		if self.high != None:
			assert n <= self.high
		b = n >> 3
		i = 0x80 >> (n & 7)

		if self.high == None and len(self.mem) <= b:
			return False
		return (self.mem[b] & i) == i

	def mtst(self, lo, hi):
		l = self.tst(lo)
		for i in range(lo, hi):
			if self.tst(i) != l:
				return None
		return l
