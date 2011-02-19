#!/usr/local/bin/python3.1
#
# A class which implements a tree of perfectly subsetting ranges
#
# This is used to partition the memory space into logical ranges
# such as "procedure", "statement", "instruction" etc.
#
# The '.a' member is where we put random properties of the nodes

import bisect

class TreeError(Exception):
	def __init__(self, t1, t2, reason):
		self.t1 = t1
		self.t2 = t2
		self.reason = "%s and %s: %s" % (t1, t2, reason)
	def __str__(self):
		return self.reason

class tree(object):
	def __init__(self, start, end, tag = "root"):
		self.start = start
		self.end = end
		self.child = list()
		self.cend = list()
		self.seq = 0
		self.a = dict()
		self.parent = None
		self.tag = tag
		self.render = None
		self.descend = True
		self.cmt = list()
		self.blockcmt = ""
		if tag == "root":
			self.nseq = 1

	def __str__(self):
		return "<Tree[0x%x...0x%x] %s #%d>" % \
		    (self.start, self.end, self.tag, self.seq)

	# Recursively descend the tree, and create a new node
	#
	# 'above' controls behaviour if we encounter an node which has
	# the same (start,end) values as we try to insert:
	# 	above == True: become parent 
	# 	above == False: become child 
	#
	def add(self, start, end, tag, above=True, t=None):
		assert start != end
		assert start >= self.start
		assert end <= self.end
		assert end > start
		if t == None:
			t = tree(start, end, tag)
			t.seq = self.nseq
			self.nseq += 1
		i = bisect.bisect(self.cend, start)
		j = i
		while j < len(self.child):
			c = self.child[j]
			if c.end <= start:
				j += 1
				i += 1
				continue
			if c.start >= end:
				break
			if c.start == start and c.end == end and above:
				pass
			elif c.start <= start and c.end >= end:
				return c.add(start, end, tag, above, t)
			elif c.start < start and c.end < end:
				raise TreeError(t, c, "Overlap(1)")
			elif c.start > start and c.end > end:
				raise TreeError(t, c, "Overlap(2)")
			j += 1
		k = i
		while k < len(self.child):
			c = self.child[k]
			if c.start >= start and c.end <= end:
				t.child.append(c)
				t.cend.append(c.end)
				del self.child[k]
				del self.cend[k]
				continue
			k += 1
		self.child.insert(i, t)
		self.cend.insert(i, end)
		t.parent = self
		return t

	def __fnd(self, start, tag):
		for i in self.child:
			if i.start == start and i.tag == tag:
				return i
			if start >= i.start and start <= i.end and len(i.child):
				j = i.__fnd(start.tag)
				if j != None:
					return j
		return None

	def find(self, start, tag):
		i = bisect.bisect_right(self.cend, start)
		if i < 0 or i >= len(self.child):
			print("FIND ??", start, tag, i)
			return None
		x = self.child[i]
		if x.start == start and x.tag == tag:
			return x
		return x.__fnd(start, tag)

	# Return a list of gaps
	def gaps(self):
		p = self.start
		l = list()
		for i in self.child:
			if p < i.start:
				l.append((p, i.start))
			else:
				assert p == i.start
			p = i.end
		if p < self.end:
			l.append((p, self.end))
		return l

	def recurse(self, func=None, priv=None, lvl=0):
		retval = False
		if func == None:
			i = "           "[0:2*lvl]
			s = "%s %s" % (i , self)
			for j in self.a:
				s += "  %s = %s" % (j, self.a[j])
			for j in self.cmt:
				s += "  ; %s" % j
			print(s)
			
		elif func(self, priv, lvl):
			retval = True
		for i in self.child:
			if i.recurse(func, priv, lvl + 1):
				retval = True
		return retval

def sanity(self, priv=None, lvl=0):
	for i in self.child:
		assert i.start >= self.start
		assert i.end <= self.end

if __name__ == "__main__":

	t = tree(0, 1000)
	t.add(100,200, "a")
	t.add(100,200, "b")
	t.add(100,200, "c", False)
	t.add(700,800, "d")
	t.add(300,400, "e")
	t.add(150,180, "f")
	t.add(150,170, "g")
	t.add(170,180, "h")
	t.add(160,161, "i")
	x = t.add(50,550, "j")
	try:
		x = t.add(50,350, "A")
		raise TreeError(t, x, "Should not work")
	except:
		pass
	try:
		x = t.add(150,550, "B")
		raise TreeError(t, x, "Should not work")
	except:
		pass
	t.recurse()
	t.recurse(sanity)
	print(t)
	print(t.gaps())
