#!/usr/local/bin/python
#

from __future__ import print_function

# Python dist imports
import sys
import random

# PyRevEng imports
import tree

class render(object):
	def __init__(self, p, lw=10, iw = 48, cw=32):
		self.p = p
		self.m = p.m
		self.t = p.t
		self.indent = ""
		self.gaps = 0
		# Label Width:
		self.lw = lw
		# Instruction Width:
		self.iw = iw
		# Comment Width:
		self.cw = cw

		# Block Cmt sep line

		s = ";"
		while len(s) < self.lw + self.iw + self.cw:
			s += "-"
		self.bcl = s + "\n"

	###############################################################
	# Rendering
	#
	def __pad_to(self, r, w):
		while len(r.expandtabs()) <= w - 8:
			r += "\t"
		while len(r.expandtabs()) < w:
			r += " "
		return r

	def __fmt(self, fo, b, l, s, c):
		n = len(b)
		if len(l) > n:
			n = len(l)
		if len(s) > n:
			n = len(s)
		if len(c) > n:
			n = len(c)
		for i in range(0, n):
			ff = ""
			if i < len(b):
				ff += b[i].expandtabs()
			ff = ff.ljust(self.col1w)
			if i < len(l):
				ff += l[i].expandtabs()
			ff = ff.ljust(self.col1w + self.lw)
			if i < len(s):
				ff += s[i].expandtabs()
			ff = ff.ljust(self.col1w + self.lw + self.iw)
			if i < len(c):
				ff += "; " + c[i].expandtabs()
			fo.write(ff + "\n")

	def __render_xxx(self, start, end, fo, lvl):
		c1 = self.m.col1(self, start, end, lvl)
		c2 = self.m.col2(self, start, end, lvl)
		self.__fmt(fo, c1, (), c2, ())
		self.gaps += end - start

	# 'xxx' render readable locations in this gap
	def __render_gaps(self, start, end, fo, lvl):
		if start == end:
			return
		s = False
		j = start
		while j < end:
			try:
				x = self.m.rd(j)
				if s == False:
					s = j
				j += 1
			except:
				if s != False:
					self.__render_xxx(s, j, fo, lvl)
				try:
					jj = self.m.next_adr(j)
					print("NA %x %x" % (j, jj))
					j = jj
				except:
					j += 1
				s = False
		if s != False:
			self.__render_xxx(s, end, fo, lvl)

	# Render, recursively, one tree node
	def __render(self, t, lvl, fo):

		if t.fold and len(t.child) > 0:
			print("WARN: tree.fold has %d children" % len(t.child))
			print("\t", t)
			t.fold = False
			t.render = None

		if t.render == None:
			fo.write("%s-%s %s\n" % (
			    self.m.afmt(t.start), self.m.afmt(t.end), t.tag))

		if t.blockcmt != "":
			for i in t.blockcmt[:-1].split("\n"):
				if i == "-":
					fo.write(self.col1s + self.bcl)
				else:
					fo.write(self.col1s + "; " + i + "\n")

		if t.render == None:
			a = t.start
			for i in t.child:
				self.__render_gaps(a, i.start, fo, lvl)
				self.__render(i, lvl + 1, fo)
				a = i.end
			self.__render_gaps(a, t.end, fo, lvl)
			return

		if type(t.render) == str:
			s = t.render.split("\n")
		else:
			try:
				s = t.render(self.p, t)
			except:
				print("Render failed " +
				    self.p.m.afmt(t.start), t.render)
				assert False

		b = self.m.col1(self, t.start, t.end, lvl)
		l = ()
		if t.start in self.p.label:
			lx = self.p.label[t.start]
			if len(lx) + 2 < self.lw:
				l = (lx + ":",)
			else:
				ff = "".ljust(self.col1w)
				ff += lx + ":\n"
				fo.write(ff)
		c = t.cmt
		if t.fold:
			x = len(l)
			if len(s) > x:
				x = len(s)
			if len(c) > x:
				x = len(c)
			if x + 1 < len(b):
				b1 = b[0:x]
				#b1.append(b[-1])
				b = b1

		self.__fmt(fo, b, l, s, c)

	def render(self, fname="-", start = None, end = None):

		if fname == "-":
			fo = sys.stdout
		else:
			fo = open(fname, "w")

		if start == None:
			start = self.m.start

		if end == None:
			end = self.m.end

		# XXX: do something with start & end

		# Calculate space string for non-col1 lines
		# XXX: hackish:

		xx = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		for i in range (0,100):
			a = int(random.random() * (end - start) + start)
			try:
				a = self.m.next_adr(a)
			except:
				pass
			try:
				self.m.rd(a)
				xx = self.m.col1(self, a, a + 1, 0)[0]
			except:
				continue
			break
		self.col1w = len(xx.expandtabs())
		self.col1s = self.__pad_to("", self.col1w)
		self.col1c = self.__pad_to("", self.p.cmt_start)

		self.__render(self.t, 0, fo)

		print("%d locations xxx'ed" % self.gaps)

		fo.close()

	#----------------------------------------------------------------------
	def __addflow(self, t, priv=None, lvl=0):
		if not 'flow' in t.a:
			return
		s = ""
		for i in t.a['flow']:
			if s != "":
				s += " "
			if type(i[2]) == int:
				d = self.p.m.afmt(i[2])
			else:
				d = str(i[2])
			if i[0] == "cond":
				s += ">:" + i[1] + ":" + d
			elif i[0] == "call":
				s += "C:" + i[1] + ":" + d
			elif i[0] == "ret":
				s += "R:" + i[1] + ":" + d
			else:
				s += str(i)
			if len(s) > 40:
				t.cmt.append(s)
				s = ""
			
		if len(s) > 0:
			t.cmt.append(s)
		
	def add_flows(self):
		self.p.t.recurse(self.__addflow)
