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

		# @render
		self.__cmt_start = 56

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
		if 'jmp' in t.a:
			n = False
			self.__bbend[t.start] = "jmp"
			for i in t.a['jmp']:
				if i != None:
					#print("JMP 0x%x" %  i)
					self.__bbstart[i] = "jmp"
					self.todo(i, func, priv)
		if 'cond' in t.a:
			n = False
			self.__bbend[t.start] = "cond"
			for i in t.a['cond']:
				if i != None:
					#print("COND 0x%x" % i)
					self.__bbstart[i] = "cond"
					self.todo(i, func, priv)
		if 'call' in t.a:
			for i in t.a['call']:
				if i != None:
					#print("CALL 0x%x" % i)
					self.__bbstart[i] = "call"
					self.todo(i, func, priv)
		if 'ret' in t.a:
			n = False
			self.__bbend[t.start] = "ret"
		if n:
			self.todo(t.end, func, priv)

	def build_bb(self):
		print("BUILD_BB")
		for i in self.__bbstart:
			if i in self.__bbx:
				continue
			x = self.__bbstart[i]
			print("%04x { %s" % (i, str(x)))
			y = self.t.find(i, None, "ins")
			if y == None:
				print("NO y %x" % i)
				continue
			while True:
				j = y.end
				if y.start in self.__bbend:
					break
				y = self.t.find(j, None, "run")
				if y != None:
					break
				y = self.t.find(j, None, "ins")
				if y == None:
					j = None
					break
				if y.start in self.__bbstart:
					break
			if j != None:
				print("RUN %x..%x" % (i,j))
				x = self.t.add(i,j,"run")
				x.blockcmt += "\n"
				self.__bbx[i] = x

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
			self.__f2(s, j, fo, lvl)
		s = False

	def __r(self, t, lvl, fo):
		if t.blockcmt != "":
			for i in t.blockcmt[:-1].split("\n"):
				fo.write("\t\t\t; " + i + "\n")

		if t.descend == True and len(t.child) > 0:
			a = t.start
			for i in t.child:
				self.__f(a, i.start, fo, lvl)
				self.__r(i, lvl + 1, fo)
				a = i.end
			self.__f(a, t.end, fo, lvl)
			return

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

		a = t.render(self, t, lvl)
		b = self.m.col1(self, t.start, t.end, lvl)
		c = t.cmt
		i = 0
		w = len(b[0])
		while True:
			r = ""
			if i >= len(b) and i >= len(a) and i >= len(c):
				break
			if i >= len(b):
				r += "%s" % "                         "[0:w]
			else:
				r += b[i]
			if i < len(a):
				r += a[i]
			while len(r.expandtabs()) < self.__cmt_start:
				r += "\t"
			if i < len(c):
				r += "; " + c[i]
			fo.write(r.strip() + "\n")
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
