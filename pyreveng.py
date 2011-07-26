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

		# @bb
		self.__bbstart = dict()
		self.__bbend = dict()
		self.__bbx = dict()

		# @label
		self.label = dict()

		# @render
		self.cmt_start = 56
		self.gaps = 0
		self.indent = ""
		self.cautions = 0

		# Random attributes
		self.a = dict()

	###############################################################
	# TODO list processing
	#

	def todo(self, adr, func, priv = None):
		assert type(adr) == int
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
				c[1](self, c[0], c[2])
				continue
			try:
				c[1](self, c[0], c[2])
			except:
				print("FAILED %x" % c[0], c)	
				
		return True

	###############################################################
	# Basic Block analysis
	#

	# Register an instruction that goes places
	def ins(self, t, func, priv = None):

		t.descend = False

		if type(t.a['mne']) != str:
			print("XXX: Fail ins, mne != str @%x", t.start)
		if not 'flow' in t.a:
			self.todo(t.end, func, priv)
			return

		for i in t.a['flow']:
			if i[0] == "call":
				self.todo(t.end, func, priv)
			else:
				ax = t.start
				if not ax in self.__bbend:
					self.__bbend[ax] = list()
				self.__bbend[ax] += (i,)

			if i[2] != None:
				ax = i[2]
				if not ax in self.__bbstart:
					self.__bbstart[ax] = list()
				self.__bbstart[ax] += ((i[0], i[1], t.start),)
				self.todo(ax, func, priv)

	def markbb(self, ax, why):
		if not ax in self.__bbstart:
			self.__bbstart[ax] = list()
		self.__bbstart[ax] += (why,)

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
			try:
				self.m.chkadr(i)
			except:
				continue
			fo = ()
			try:
				y = self.t.find(i, "ins")
			except:
				continue
			if y == None:
				continue
			while True:
				if 'flow' in y.a:
					fo += y.a['flow']
				j = y.end
				if y.start in self.__bbend:
					break
				if y.end in self.__bbstart:
					fo += (("nxt", "T", y.end),)
					break
				try:
					y = self.t.find(j, "ins")
				except:
					j = None
					break
				if y == None:
					j = None
					break
			if j != None:
				try:
					x = self.t.add(i,j,"run")
					#x.blockcmt += "\n"
					x.a['flow_in'] = self.__bbstart[i]
					x.a['flow'] = fo
					self.__bbx[i] = x
				except:
					print("Fail to add run %x,%x" % (i,j))

	# Eliminate trampolines, such as calls to absolute unconditional
	# jumps in order to extend reach of addressing modes.

	def __elim(self, t, p, l):
		if t.tag != "run":
			return
		if len(t.child) != 1:
			return
		if len(t.a['flow_in']) == 0:
			return
		fl = t.a['flow']
		if len(fl) != 1:
			return
		if fl[0][0] != "cond":
			return
		if fl[0][1] != "T":
			return
		if fl[0][2] == "None":
			return

		try:
			dst = self.t.find(fl[0][2], "run")
			if dst == None:
				return
		except:
			return

		# Remove trampoline from destination flow_in
		dfi = dst.a['flow_in']
		for i in range(0, len(dfi)):
			if dfi[i][2] == t.start:
				del dfi[i]
				break

		# Move in-flows to destination
		for i in t.a['flow_in']:
			dfi += (i,)

		t.a['flow_in'] = ()
		# XXX: HACK:
		t.child[0].cmt.append("Trampoline")
		return True

	def eliminate_trampolines(self):
		while self.t.recurse(self.__elim):
			continue



	def __build_func(self, a):
		done = dict()
		todo = dict()
		l = list()

		t = self.t.find(a, "run")
		done[a] = t
		sa = t.start
		ea = t.end
		la = t.end
		y = t
		while True:
			if y == None:
				print("BUILD_FUNC: " + self.m.afmt(a))
				print("FAIL (y = None)")
				return
			if y.start < sa:
				print("BUILD_FUNC: " + self.m.afmt(a))
				print("FAIL start before entry %x < %x" % (y.start, sa), y)
				return
			if y.end > ea:
				ea = y.end
			for i in y.a['flow']:
				if i[0] == "call":
					continue
				if i[2] == None:
					continue
				if i[2] in done:
					continue
				if i[2] in todo:
					continue
				todo[i[2]] = True
				l.append(i[2])
			for i in y.a['flow_in']:
				if i[0] == "call" and y.start == sa:
					continue
				if i[2] == None:
					print("BUILD_FUNC: " + self.m.afmt(a))
					print("FAIL flow_in <none>", i)
					return
				if i[2] < sa:
					print("BUILD_FUNC: " + self.m.afmt(a))
					print("FAIL flow_in before entry %x < %x" % (i[2], sa), i)
					return
				if i[2] > la:
					la = i[2]
			if len(l) == 0:
				break
			xa = l.pop()
			del todo[xa]
			y = self.t.find(xa, "run")
			done[xa] = y
		if la > ea:
			print("BUILD_FUNC: " + self.m.afmt(a))
			print("FAIL flow_in from beyond end %x > %x" % (la, ea))
			return
		try:
			x = self.t.add(sa, ea, "proc")
		except:
			return
		x.blockcmt += "\n-\n"
		x.blockcmt += "Procedure %x..%x\n" % (sa, ea)
		x.a['indent'] = True
		#x.a['flow_in'] = t.a['flow_in']
		for i in x.child:
			if not i.start in done:
				print("BUILD_FUNC: " + self.m.afmt(a))
				print("ORPHAN", i)
			else:
				i.a['in_proc'] = True
		return x

	def __recurse_proc(self, t, p, l):
		if t.tag != "run":
			return
		if 'in_proc' in t.a:
			return
		if not 'flow_in' in t.a:
			return
		for i in t.a['flow_in']:
			if i[0] == "call":
				self.__build_func(t.start)
				return True

	def build_procs(self, t = None):
		if t == None:
			t = self.t
		t.recurse(self.__recurse_proc)

	###############################################################

	def setlabel(self, a, lbl):
		self.label[a] = lbl

	###############################################################
	# Resolve effective addresses that go through unconditional jumps
	#

	def resolve_ea(self, a):
		while True:
			if a == None:
				return None
			try:
				self.m.chkadr(a)
			except:
				return None
			try:
				x = self.t.find(a, "ins")
			except:
				return a
			if x == None:
				return a
			if not 'flow' in x.a:
				return a
			y = x.a['flow']
			if len(y) == 0:
				return a
			if len(y) > 1:
				return a
			if y[0][0] != "cond":
				return a
			if y[0][1] != "T":
				return a
			if y[0][2] == a:
				return a
			a = y[0][2]

	###############################################################
	# Rendering
	#

	def __render_ea(self, adr, cond):
		if cond != None:
			t = "EA(%s)=" % cond
		else:
			t = "EA="
		adr = self.resolve_ea(adr)
		if adr == None:
			t += "?"
		else:
			t += self.m.afmt(adr)
			if adr in self.label:
				t += "/" + self.label[adr]
		return t
		
	# Emit effective address comments
	def __render_ea_cmt(self, t, c):
		s = ""
		d = ""
		if 'flow' in t.a:
			for x in t.a['flow']:
				if x[2] != None:
					s += d + self.__render_ea(x[2], x[0] + "," + x[1])
					d = ", "
		if 'EA' in t.a:
			# XXX: multiple EA's per instrution, how ?
			for ii in t.a['EA']:
				s += d + self.__render_ea(ii, None)
				d = ", "
		if s != "":
			c.append(s)

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
