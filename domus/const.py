#!/usr/local/bin/python
#

import tree
import mem

class word(tree.tree):
	def __init__(self, p, adr, fmt = "%d"):
		tree.tree.__init__(self, adr, adr + 1, "word")
		p.t.add(adr, adr + 1, "word", True, self)
		self.fmt = fmt
		self.render = self.rfunc

	def rfunc(self, p, t):
		try:
			x = p.m.rd(t.start)
		except:
			return ()
		if x in p.label:
			return ((".word\t" + p.label[x]),)
		q = p.m.rdqual(t.start)
		if q == 3:
			return ((".word\t" + p.m.afmt(x/2) + "*2"),)
		elif q == 2 or q == 7:
			return ((".word\t" + p.m.afmt(x)),)
		else:
			return ((".word\t" + self.fmt) % x, )

class dot_txt(tree.tree):
	def __init__(self, p, start, end):
		if end == None:
			end = start
			while True:
				a = p.m.rd(end)
				if a & 0xff == 0:
					break
				if a >> 8 == 0:
					break
				end += 1
		tree.tree.__init__(self, start, end, "dot_txt")
		p.t.add(start, end, "dot_txt", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t):
		s = ".TXT\t'"
		for i in range(t.start, t.end):
			q = p.m.rdqual(i)
			if q != 1:
				raise DomusError(t.start, ".TXT is relocated")
			x = p.m.rd(i)
			y = x >> 8
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
			y = x & 0xff
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
		s += "'"
		return (s,)
