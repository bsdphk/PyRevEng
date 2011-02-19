#!/usr/local/bin/python
#
# This is the central container-class for a PyRevEng job.
#
# Services rendered:
#	todo	Todo list, things to do, one thing after another
#	bb	Basic Block analysis of instructions
#	render	Rendering
#
# Mandatory public members:
#	.m	= memory, instance of mem.py
#	.t	= tree, instance of tree.py
#

from __future__ import print_function

# Python dist imports
import sys
import random

# PyRevEng imports
import tree

class pyreveng(object):
	def __init__(self, m, t=None):
		self.m = m
		if t == None:
			t = tree.tree(m.start, m.end)
		self.t = t

		# @todo
		self.__tlist = list()
		self.__did = dict()

		# @bb
		self.__bbstart = dict()
		self.__bbend = dict()
		self.__bbx = dict()

		# @label
		self.__label = dict()

		# @render
		self.cmt_start = 56

	###############################################################
	# TODO
	#

	def todo(self, adr, func, priv = None):
		self.__tlist.append((adr, func, priv))

	def run(self):
		if len(self.__tlist) == 0:
			return False
		while len(self.__tlist) > 0:
			c = self.__tlist[0]
			del self.__tlist[0]
			if c in self.__did:
				continue
			self.__did[c] = True
			#print(">>> 0x%x" % c[0])
			c[1](self, c[0], c[2])
		self.build_bb()
		return True

	###############################################################
	# Basic Block analysis
	#

	# Register an instruction that goes places
	def ins(self, t, func, priv = None):
		#print("INS", t)
		n = True
		if 'cond' in t.a:
			n = False
			self.__bbend[t.start] = "cond"
			for i in t.a['cond']:
				#print("COND", i)
				if i[1] != None:
					self.__bbstart[i[1]] = "cond"
					self.todo(i[1], func, priv)
		if 'call' in t.a:
			for i in t.a['call']:
				#print("CALL", i)
				if i[1] != None:
					self.__bbstart[i[1]] = "call"
					self.todo(i[1], func, priv)
		if 'ret' in t.a:
			n = False
			self.__bbend[t.start] = "ret"
		if n:
			self.todo(t.end, func, priv)

	def markbb(self, a, why):
		self.__bbstart[a] = why

	# Build runs of instructions.
	#
	# A run is defined as a sequence of one or more instructions which
	# are executed as a unit, either all are executed, or none are.
	#
	# Instructions which transfer control elsewhere (jmp, cond branch,
	# return &c) will always terminate a run, and will thereby define
	# the beginning of the next run.
	#
	# NB: conditionals which always take one path can screw up this logic.
	#
	def build_bb(self):
		for i in self.__bbstart:
			if i in self.__bbx:
				continue
			x = self.__bbstart[i]
			y = self.t.find(i, "ins")
			if y == None:
				continue
			while True:
				j = y.end
				if y.start in self.__bbend:
					break
				y = self.t.find(j, "run")
				if y != None:
					break
				y = self.t.find(j, "ins")
				if y == None:
					j = None
					break
				if y.start in self.__bbstart:
					break
				if 'ret' in y.a:
					j = y.end
					break
				if 'jmp' in y.a:
					j = y.end
					break
				if 'cond' in y.a:
					j = y.end
					break
			if j != None:
				x = self.t.add(i,j,"run")
				x.blockcmt += "\n"
				self.__bbx[i] = x

	###############################################################

	def setlabel(self, a, lbl):
		self.__label[a] = lbl

	###############################################################
	# Resolve effective addresses that go through unconditional jumps
	#

	def resolve_ea(self, a):
		while True:
			if a == None:
				return None
			x = self.t.find(a, "ins")
			if x == None:
				return a
			if not 'cond' in x.a:
				return a
			y = x.a['cond']
			if len(y) > 1:
				return a
			if y[0][1] == None:
				return a
			if y[0][0] != "T":
				return a
			if y[0][1] == a:
				return a
			a = y[0][1]

	###############################################################
	# Rendering
	#

	def __f2(self, a, b, fo, lvl):
		for i in self.m.col1(self, a, b, lvl):
			fo.write(i + ".XXX\n")

	def __f(self, a, b, fo, lvl):
		if a == b:
			return
		s = False
		for j in range(a, b):
			try:
				x = self.m.rd(j)
				if s == False:
					s = j
			except:
				if s != False:
					self.__f2(s, j, fo, lvl)
				s = False
				continue
		if s != False:
			self.__f2(s, b, fo, lvl)
		s = False

	def __eas(self, adr, cond):
		if cond != None:
			t = "EA(%s)=" % cond
		else:
			t = "EA="
		adr = self.resolve_ea(adr)
		if adr == None:
			t += "?"
		else:
			t += self.m.afmt(adr)
			if adr in self.__label:
				t += "/" + self.__label[adr]
		return t
		
	# Emit effective address comments
	def __ear(self, t, c):
		s = ""
		d = ""
		for jj in ('cond', 'call'):
			if not jj in t.a:
				continue
			x = t.a[jj]
			if len(x) == 1 and x[0][0] == "T":
				s += d + self.__eas(x[0][1], None)
				d = ", "
			else:
				for ii in x:
					s += d + self.__eas(ii[1], ii[0])
					d = ", "
		if 'EA' in t.a:
			# XXX: multiple EA's per instrution, how ?
			for ii in t.a['EA']:
				s += d + self.__eas(ii, None)
				d = ", "
		if s != "":
			c.append(s)

	def __r(self, t, lvl, fo):
		if t.blockcmt != "":
			for i in t.blockcmt[:-1].split("\n"):
				if i != "":
					fo.write(self.col1s + "; " + i + "\n")
				else:
					fo.write("\n")

		if t.descend == True and len(t.child) > 0:
			a = t.start
			for i in t.child:
				self.__f(a, i.start, fo, lvl)
				self.__r(i, lvl + 1, fo)
				a = i.end
			self.__f(a, t.end, fo, lvl)
			return

		if t.start in self.__label:
			fo.write(self.col1s + self.__label[t.start] + ":\n")

		if t.render == None:
			fo.write("%s" % self.m.afmt(t.start))
			if t.end > t.start + 1:
				fo.write("-%s" % self.m.afmt(t.end - 1))
			fo.write(" %s " % t.tag)
			for i in t.a:
				fo.write(" %s = %s" % (i, str(t.a[i])))
			fo.write("\n")
			if self.m.tstflags(t.start, t.end, self.m.undef):
				fo.write("<undef>\n")
				return
			for i in self.m.col1(self, t.start, t.end, lvl):
				fo.write(i)
				fo.write("\n")
			return

		if type(t.render) == str:
			a = (t.render,)
		else:
			a = t.render(self, t, lvl)
		b = self.m.col1(self, t.start, t.end, lvl)
		c = t.cmt
		self.__ear(t, c)

		i = 0
		w = len(b[0])
		while True:
			r = ""
			if i >= len(b) and i >= len(a) and i >= len(c):
				break
			if i >= len(b):
				r += self.col1s
			else:
				r += b[i]
			if i < len(a):
				r += a[i]
			while len(r.expandtabs()) < self.cmt_start - 8:
				r += "\t"
			while len(r.expandtabs()) < self.cmt_start:
				r += " "
			if i < len(c):
				r += "; " + c[i]
			fo.write(r.rstrip() + "\n")
			i += 1
		

	def render(self, fname="-", start = None, end = None):

		if fname == "-":
			fo = sys.stdout
		else:
			fo = fopen(fname, "w")

		if start == None:
			start = self.m.start

		if end == None:
			end = self.m.end

		# XXX: do something with start & end

		# Calculate space string for non-col1 lines
		# XXX: hackish:

		while True:
			a = int(random.random() * (end - start) + start)
			try:
				self.m.rd(a)
			except:
				continue
			break
		xx = self.m.col1(self, a, a + 1, 0)[0]
		self.col1w = len(xx.expandtabs())
		self.col1s = ""
		for i in range(0, self.col1w/8):
			self.col1s += "\t"
		for i in range(0, self.col1w & 7):
			self.col1s += " "

		self.__r(self.t, 0, fo)

	# A general purpose hexdumping routine
	def hexdump(self, start = None, end = None, fo = sys.stdout, wid=16):
		if start == None:
			start = self.m.start

		if end == None:
			end = self.m.end

		# Must be power of two
		assert wid & (wid -1) == 0

		adr = start
		while adr < end:
			s = self.m.afmt(adr)
			s += " "
			t = ""
			b = adr & ~(wid -1)
			e = b + wid
			if e > end:
				e = end
			if self.m.tstflags(b, e, self.m.undef):
				adr = b + wid
				continue
			for i in range(0, wid):
				if i == 8:
					s += " " 

				if i < (adr & (wid-1)) or b + i >= end:
					s += " .."
					t += "."
					continue
				try:
					x = self.m.rd(b + i)
				except:
					s += " --"
					t += "-"
					continue

				s += " %02x" % x
				if x >= 32 and x <= 126:
					t += "%c" % x
				else:
					t += "."
			s += "  |" + t + "|\n"
			fo.write(s)
			adr = b + 16
