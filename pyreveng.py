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
	def __init__(self, m, lo=None, hi=None):
		""" The container class for a reverse engineering task.

		m:
			A memory class
		lo:
			The lowest address of interest
		hi:
			The higest address of interest
		"""

		self.m = m
		self.lo = lo
		self.hi = hi
		if self.lo == None:
			self.lo = m.start
		if self.hi == None:
			self.hi = m.end
		assert type(self.lo) == int
		assert type(self.hi) == int

		self.t = tree.tree(self.lo, self.hi)

		self.c = dict()

		# @todo
		self.__tlist = list()

		# @label
		self.label = dict()

		# Random attributes
		self.a = dict()

		# @hints
		self.hints = dict()

		self.cmt_start = 56

	###############################################################
	# HINT processing
	#
	def hint(self, adr):
		if not adr in self.hints:
			self.hints[adr] = dict()
		return self.hints[adr]

	###############################################################
	# TODO list processing
	#

	def todo(self, adr, func, priv = None):
		assert type(adr) == int
		if adr < self.lo or adr > self.hi:
			print("WARNING: Ignoring todo at " +
			    self.m.afmt(adr), func, priv)
		try:
			self.m.chkadr(adr)
		except:
			return
		self.__tlist.append((adr, func, priv))

	def run(self):
		if len(self.__tlist) == 0:
			return False
		while len(self.__tlist) > 0:
			c = self.__tlist[0]
			del self.__tlist[0]
			#print(">>> 0x%x" % c[0])
			if True:
				c[1](c[0], c[2])
				continue
			try:
				c[1](c[0], c[2])
			except:
				print("FAILED %x" % c[0], c)	
				
		return True

	###############################################################

	def setlabel(self, a, lbl):
		self.label[a] = lbl

	###############################################################
	# Load labels from file
	#

	def loadlabels(self, filename):
		fi = open(filename, "r")
		for i in fi.readlines():
			i = i.strip()
			if i == "" or i[0] == "#":
				continue
			j = i.split()
			self.setlabel(int(j[1], 0), j[0])
		fi.close()

	###############################################################
	# A general purpose hexdumping routine
	#

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
