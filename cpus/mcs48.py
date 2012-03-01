#!/usr/local/bin/python
#
# Intel MCS 48 family disassembler
#

import instree
import disass

#######################################################################

class mcs48(disass.assy):

	def __init__(self, p, name = "mcs48"):
		disass.assy.__init__(self, p, name)
		self.root = instree.instree(
		    width = 8,
		    filename = __file__[:-3] + "_instructions.txt"
		)

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		p = self.p

		# By default...
		ins.hi = ins.lo + 1

		#print(">>> @%04x" % adr, "%02x" % p.m.rd(adr))
		c = self.root.find(p, adr, p.m.rd)
		assert c != None
		#print(">>>> ", c, "wid",c.width)
		ins.hi = ins.lo + (c.width >> 3)
		ins.mne = c.spec[0]
		ins.oper = list()
		for i in c.spec[1].split(","):
			if i == "laddr":
				hi = c.get_field(p, adr, p.m.rd, 1, "ahi")
				lo = c.get_field(p, adr, p.m.rd, 1, "alow")
				da = (hi << 8) | lo
				ins.oper.append("0x%03x" % da)
			elif i == "addr":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				da = adr & ~0xff
				da |= j
				ins.oper.append("0x%03x" % da)
			elif i == "@A":
				ins.oper.append(i)
				da = None
			elif i == "@Rr":
				j = c.get_field(p, adr, p.m.rd, 1, "r")
				ins.oper.append("@R%d" % j)
			elif i == "Rr":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("R%d" % j)
			elif i == "Pp":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("P%d" % j)
			elif i == "data":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("#0x%02x" % j)
				
			elif i == "b":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.mne = "JP%d" % j
			elif i in ("T", "PSW", "F1", "F0", "TCNT", "BUS",
			    "A", "C", "RB1", "RB0", "TCNTI", "I", "CLK",
			    "MB0", "MB1"):
				ins.oper.append(i)
			elif i == "-":
				pass
			else:
				print("MISS", i, c)
				ins.oper.append(i)
		if ins.mne == "JMP":
			ins.flow("cond", "T", da)
		elif ins.mne == "CALL":
			ins.flow("call", "T", da)
		elif ins.mne[0] == "J":
			ins.flow("cond", ins.mne[1:], da)
			ins.flow("cond", "N" + ins.mne[1:], ins.hi)
		elif ins.mne == "DJNZ":
			ins.flow("cond", "NZ", da)
			ins.flow("cond", "Z", ins.hi)
		elif ins.mne == "RET":
			ins.flow("ret", "T", None)
		elif ins.mne == "RETR":
			ins.flow("ret", "T", None)
		
