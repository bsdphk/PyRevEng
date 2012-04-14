#!/usr/local/bin/python
#
# Zilog Z-80 disassembler
#

import instree
import disass

#######################################################################

class z80(disass.assy):

	def __init__(self, p, name = "z80"):
		disass.assy.__init__(self, p, name)
		self.root = instree.instree(
		    width = 8,
		    filename = __file__[:-3] + "_instructions.txt"
		)
		self.io_port = dict()

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
		#ins.oper = list(c.spec[1].split(","))
		cc = "T"
		da = None
		for i in c.spec[1].split(","):
			if i == "nn":
				hi = c.get_field(p, adr, p.m.rd, 1, "n2")
				lo = c.get_field(p, adr, p.m.rd, 1, "n1")
				da = (hi << 8) | lo
				ins.oper.append((da, "%s", "0x%04x" % da))
			elif i == "(nn)":
				hi = c.get_field(p, adr, p.m.rd, 1, "n2")
				lo = c.get_field(p, adr, p.m.rd, 1, "n1")
				da = (hi << 8) | lo
				ins.oper.append((da, "%s", "(0x%04x)" % da))
			elif i == "cc":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				cc = (
				    "NZ", "Z", "NC", "C", "PO", "PE", "P", "M"
				    )[j]
				ins.oper.append(cc)
			elif i == "dd":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append(("BC", "DE", "HL", "SP")[j])
			elif i == "(i)" or i == "(o)":
				j = c.get_field(p, adr, p.m.rd, 1, "io")
				if j in self.io_port:
					k = self.io_port[j]
					if len(k) == 2 and i == "(i)":
						ins.oper.append("(%s)" % k[0])
					elif len(k) == 2 and i == "(o)":
						ins.oper.append("(%s)" % k[1])
					else:
						ins.oper.append("(%s)" % k)
				else:
					ins.oper.append("(0x%02x)" % j)
			elif i == "(o)":
				j = c.get_field(p, adr, p.m.rd, 1, "i")
				if j in self.io_port:
					k = self.io_port[j]
					if len(k) == 2:
						ins.oper.append("(%s)" % k[0])
					else:
						ins.oper.append("(%s)" % k)
				else:
					ins.oper.append("(0x%02x)" % j)
			elif i == "n":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("0x%02x" % j)
			elif i == "qq":
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append(("BC", "DE", "HL", "AF")[j])
			elif i in ("rd", "rs"):
				j = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append((
				    "B", "C", "D","E", "H", "L", None, "A"
				    )[j])
			elif i in (
			    "HL",
			    "A",
			    "DE",
			    "SP",
			    "I",
			    "0",
			    "1",
			    "2",
			    "(HL)",
			    "(DE)",
			    "(BC)",
			    ):
				ins.oper.append(i)
			elif i == "-":
				pass
			else:
				print("MISS", i, c)
				ins.oper.append(i)
		if ins.mne == "RET":
			ins.flow("ret", "I", None)
		elif ins.mne == "RETI":
			ins.flow("ret", "I", None)
		elif ins.mne == "JP":
			ins.flow("cond", cc, da)
			if cc != "T":
				ins.flow("cond", "!" + cc, ins.hi)
		elif ins.mne == "JR":
			ins.flow("cond", cc, da)
			if cc != "T":
				ins.flow("cond", "!" + cc, ins.hi)
		elif ins.mne == "CALL":
			ins.flow("call", cc, da)
			if cc != "T":
				ins.flow("cond", "!" + cc, ins.hi)
