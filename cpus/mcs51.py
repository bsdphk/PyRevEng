#!/usr/local/bin/python
#
# Intel MCS 51 family disassembler
#

import instree
import disass

#######################################################################

class mcs51(disass.assy):

	def __init__(self, p, name = "mcs51"):
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

		print(">>> @%04x" % adr, "%02x" % p.m.rd(adr))
		c = self.root.find(p, adr, p.m.rd)
		assert c != None
		print(">>>> ", c, "wid",c.width)
		ins.hi = ins.lo + (c.width >> 3)
		ins.mne = c.spec[0]
		ins.oper = list()
		for i in c.spec[1].split(","):
			if i == "a16":
				hi = c.get_field(p, adr, p.m.rd, 1, "ahi")
				lo = c.get_field(p, adr, p.m.rd, 1, "alo")
				da = (hi << 8) | lo
				ins.oper.append((da, "%s", "0x%03x" % da))
			elif i == "addr11":
				hi = c.get_field(p, adr, p.m.rd, 1, "ahi")
				lo = c.get_field(p, adr, p.m.rd, 1, "alo")
				da = (hi << 8) | lo
				da |= ins.hi & 0xf800
				ins.oper.append((da, "%s", "0x%03x" % da))
			elif i == "arel":
				rel = c.get_field(p, adr, p.m.rd, 1, i)
				if rel & 0x80:
					rel -= 256
				da = ins.hi + rel
				ins.oper.append((da, "%s", "0x%03x" % da))
			elif i in ("A", "DPTR"):
				ins.oper.append(i)
				continue
			elif i == "-":
				continue
			else:
				ins.oper.append("??" + i)
				print("???", i)
		if ins.mne in ("LJMP", "SJMP", "AJMP"):
			ins.flow("cond", "T", da)
		elif ins.mne in ("JB", "JNB", "JBC", "JC", "JNC", "JZ", "JNZ",
		    "DJNZ", "CJNE"):
			ins.flow("cond", ins.mne[1:], da)
			ins.flow("cond", "!" + ins.mne[1:], ins.hi)
		elif ins.mne == "LCALL" or ins.mne == "ACALL":
			ins.flow("call", "T", da)
		elif ins.mne == "RET":
			ins.flow("ret", "T", None)
		elif ins.mne == "RETI":
			ins.flow("ret", "I", None)
		return
