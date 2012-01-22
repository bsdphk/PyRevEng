#!/usr/local/bin/python
#

from __future__ import print_function

import sys
import bitmap
import copy

import mem

#######################################################################
#
# We report trouble as these exceptions
#

class DisassError(Exception):
        def __init__(self, reason, diag = None):
                self.reason = reason
                self.diag = diag
                self.value = (str(self.reason),)
        def __str__(self):
                return repr(self.value)

#######################################################################

class disass(object):
	"""Some kind of execution or interpretation unit.

	This will usually be a CPU, but it can also be interpreters for
	the meta-code of high level languages.
	"""
	def __init__(self, p, name):
		self.p = p
		self.name = name
		self.bm = bitmap.bitmap()
		self.ins = dict()
		p.c[name] = self
		self.fails = 0
		self.is_clone = False
		self.follow_calls = True
		self.special_dst = dict()

	def clone(self, follow_calls = True):
		"""Make a clone for exploratory purposes
		"""
		this = copy.copy(self)
		this.ins = copy.copy(this.ins)
		this.bm = copy.deepcopy(this.bm)
		this.fails = 0
		this.is_clone = True
		this.follow_calls = follow_calls
		return this

	def disass(self, adr, priv=None):
		"""Schedule the address for disassembly

		The instruction is returned immediately, but the
		disassembly may not happen until later.
		"""

		assert type(adr) == int

		if adr in self.ins:
			i = self.ins[adr]
			if i.status == "OK":
				return i
			elif i.status == "new":
				return i
			elif i.status == "prospective":
				return i
			elif self.is_clone:
				self.fails += 1
			return i

		ins = instruction(self, adr)
		self.ins[adr] = ins
		if self.bm.tst(adr):
			ins.status = "overlap"
			self.fails += 1
		else:
			ins.status = "prospective"
			self.bm.set(adr)
			self.p.todo(adr, self.xxdo_disass, ins)
		return ins

	def xxdo_disass(self, p, adr, ins):
		assert p == self.p
		if ins.status != "prospective":
			print(ins)
		assert ins.status == "prospective"
		assert self.fails != None
		if self.fails > 0 and self.is_clone:
			ins.fail("cascade")
			return
		try:
			self.do_disass(adr, ins)
		except mem.MemError as bug:
			ins.fail("no mem", str(bug))
		except DisassError as bug:
			ins.fail(bug.reason, bug.diag)
		assert self.fails != None
		self.finish_ins(ins)

	def is_ins(self, adr):
		"""Test if we have an instruction on address already
		"""
		return adr in self.ins

	def new_ins(self, adr):
		"""Create a new instruction

		Return None if it already exists
		Return False if it overlaps an existing instruction
		"""
		if adr in self.ins:
			return None

		if self.bm.tst(adr):
			return False
		i = instruction(self, adr)
		self.bm.set(adr)
		self.ins[adr] = i
		return i

	def finish_ins(self, ins):
		"""Finish the definition of an instruction

		"""
		assert type(ins.lo) == int
		assert type(ins.hi) == int

		if ins.status == "fail":
			return

		assert ins.lo >= self.p.lo
		assert ins.hi <= self.p.hi
		assert self.bm.tst(ins.lo)
		assert ins == self.ins[ins.lo]

		if ins.hi > ins.lo + 1 and \
		    self.bm.mtst(ins.lo + 1, ins.hi) != False:
			self.fails += 1
			if self.is_clone:
				return
			print("ERROR: Overlapping instructions:")
			l = list()
			ins.status = "overlap"
			self.bm.mset(ins.lo, ins.hi)
			print("\t", ins)
			l.append(ins)
			ins.overlap = l
			for j in range (ins.lo + 1, ins.hi):
				if j in self.ins:
					ii = self.ins[j]
					print("\t", ii)
					ii.status = "overlap"
					ii.overlap = l
					l.append(ii)
			return

		self.bm.mset(ins.lo, ins.hi)

		if ins.status != "prospective":
			return

		ins.status = "OK"

		# Only process flow for good instructions
		if len(ins.flow_out) == 0:
			j = self.disass(ins.hi)

		for i in ins.flow_out:
			if type(i[2]) != int:
				continue
			if not i[2] in self.special_dst:
				continue
			self.special_dst[i[2]](ins, i[2])

		has_cond = False
		for i in ins.flow_out:
			if i[0] == "cond":
				has_cond = True
				break

		for i in ins.flow_out:
			if i[0] == "call":
				if not has_cond:
					j = self.disass(ins.hi)
				if not self.follow_calls:
					continue
			if type(i[2]) != int:
				continue
			try:
				self.p.m.chkadr(i[2])
				j = self.disass(i[2])
				j.flow_in.append((i[0], i[1], ins.lo))
			except:
				pass

	def to_tree(self):
		# print("Inserting", self.name, "instructions in tree")
		for i in self.ins:
			ins = self.ins[i]
			if ins.status != "OK":
				continue
			x = self.p.t.add(ins.lo, ins.hi, "ins")
			x.render = self.render
			x.a['flow'] = ins.flow_out
			x.a['ins'] = ins
			if ins.cmt != "":
				for i in ins.cmt.split("\n"):
					x.cmt.append(i)

class assy(disass):
	"""Disassembler for ass' code

	Instructions have .mne and .oper attributes

	Render function does label resolution on .oper elements
	of the format:
		(int, "foo(%s)")
			Substitute label or m.afmt() if "%s" present
		(int, "foo(%s)", "bar(%s)")
			Substitute label in "foo(%s)" (if "%s" present)
			Substitute m.afmt() in "bar(%s)" (if "%s" present)
	"""
	def __init__(self, p, name):
		disass.__init__(self, p, name)

	def disass(self, adr, priv=None):
		assert type(adr) == int
		j = disass.disass(self, adr, priv)
		if j.status == "prospective":
			j.mne = None
			j.oper = list()
		return j

	def render(self, p, ins):

		if type(ins) != instruction:
			# transistional hack
			ins = ins.a['ins']

		assert ins.mne != None
		assert ins.status == "OK"
		s = ins.mne
		d = "\t"
		for i in ins.oper:
			s += d
			d = ","
			if type(i) == str:
				s += i
				continue
			if type(i[0]) == int:
				if i[0] in self.p.label:
					s += i[1] % self.p.label[i[0]]
				elif len(i) < 3 and i[1].find('%s') != -1:
					s += i[1] % self.p.m.afmt(i[0])
				elif len(i) < 3:
					s += i[1]
				elif i[2].find('%s') != -1:
					s += i[2] % self.p.m.afmt(i[0])
				else:
					s += i[2]
				
			else:
				s += "<XXX " + str(i) + ">"
		return (s,)

class instruction(object):
	"""A single instruction.

	"""
	def __init__(self, disass, adr):
		self.disass = disass
		self.flow_in = list()
		self.flow_out = list()
		self.render = None
		self.lo = adr
		self.hi = adr + 1
		self.model = None
		self.status = "new"
		self.cmt = ""
		self.diag = None

	def __repr__(self):
		s = "<ins " + self.disass.name + " " + str(self.status)
		s += " " + self.disass.p.m.afmt(self.lo)
		if self.hi != None:
			s += "-" + self.disass.p.m.afmt(self.hi)
		s += ">"
		return s

	def dflow(self, fl):
		s = fl[0] + ":" + fl[1] 
		if type(fl[2]) == int:
			s += ":" + self.disass.p.m.afmt(fl[2])
		elif fl[2] != None:
			s += ":" + str(fl[2])
		return s

	def lcmt(self, s):
		if len(self.cmt) > 0:
			self.cmt += "\n"
		self.cmt += s

	def debug(self):
		s = self.__repr__()

		s = s[:-1]

		if len(self.flow_in) > 0:
			t = ""
			for i in self.flow_in:
				s += " <" + self.dflow(i)
				t = " "

		if len(self.flow_out) > 0:
			t = ""
			for i in self.flow_out:
				s += " >" + self.dflow(i)
				t = " "

		if self.reason != None:
			s += " " + str(self.reason)
		s += " >"
		return s

	def flow(self, mode, cc, dst):
		self.flow_out.append((mode, cc, dst))

	def fail(self, reason, diag = None):
		assert self.status == "prospective"
		self.status = "fail"
		self.reason = reason
		if diag != None:
			self.diag = diag
		if not self.disass.is_clone:
			print("FAIL: ",  self.debug())
			if self.diag != None:
				print("\t", self.diag);
		self.disass.fails += 1
