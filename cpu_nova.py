#!/usr/local/bin/python
#
# This is a disassembler for the Data General Nova CPU
#
#	self.iodev[device_number] = "device_name"
#		Name the I/O devices
#

from __future__ import print_function

import disass
import instree

class nova(disass.assy):
	def __init__(self, p, name = "nova"):
		disass.assy.__init__(self, p, name)
		self.root = instree.instree(
		    width = 16,
		    filename = "cpus/nova_instructions.txt",
		)
		self.iodev = {
			63: "CPU",
		}

	def rdarg(self, ins, c, arg):
		return c.get_field(self.p, ins.lo, self.p.m.rd, 1, arg)

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		ins.hi = ins.lo + 1

		try:
			c = self.root.find(self.p, adr, self.p.m.rd)
		except:
			ins.fail("no memory")
			return

		ins.mne = c.spec[0]
		da = 0
		for i in c.spec[1].split(","):
			if i == "#":
				if self.rdarg(ins, c, i) != 0:
					ins.mne += "#"
			elif i == "@":
				if self.rdarg(ins, c, i) != 0:
					ins.mne += "@"
			elif i == "sh":
				ins.mne += (
				    "", "L", "R", "S"
				)[self.rdarg(ins, c, i)]
			elif i == "cy":
				ins.mne += (
				    "", "Z", "O", "C"
				)[self.rdarg(ins, c, i)]
			elif i == "skip":
				j = self.rdarg(ins, c, i)
				if j:
					ins.oper.append((
					    "",    "SKP", "SZC", "SNC",
					    "SZR", "SNR", "SEZ", "SBN"
					)[self.rdarg(ins, c, i)])
				if j > 0:
					ins.flow("cond", "T", ins.lo + 2)
				if j > 1:
					ins.flow("cond", "T", ins.lo + 1)
			elif i == "acs" or i == "acd":
				ins.oper.append("%d" % self.rdarg(ins, c, i))
			elif i == "displ":
				r = self.rdarg(ins, c, "idx")
				o = self.rdarg(ins, c, "displ")
				if r != 0 and o > 128:
					o -= 256
				if r == 0:
					ins.oper.append((
						o,
						"%s",
						self.p.m.dfmt(o, False)
					))
					da = o
				elif r == 1:
					o += ins.lo
					ins.oper.append((o, "%s"))
					da = o
				else:
					ins.oper.append(self.p.m.dfmt(o, False))
					ins.oper.append("%d" % r)
					da = None
			elif i == '""':
				pass
			else:
				print(i, c)
				ins.fail("Unhandled arg <%s>" % i)
				return

		# XXX: should also handle SKP instructions masked by macros
		if ins.mne[1:3] == "SZ" or ins.mne[:3] == "SKP":
			ins.flow("cond", "?", ins.lo + 1)
			ins.flow("cond", "?", ins.lo + 2)
		elif ins.mne == "JMP":
			ins.flow("cond", "T", da)
		elif ins.mne == "JSR":
			ins.flow("call", "T", da)
		elif ins.mne == "JMP@" or ins.mne == "JSR@":
			if da != None:
				try:
					da = self.p.m.rd(da)
				except:
					da = None
			if ins.mne == "JMP":
				ins.flow("cond", "T", da)
			else:
				ins.flow("call", "T", da)
