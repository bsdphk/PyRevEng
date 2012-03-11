#!/usr/local/bin/python
#
# Intel MCS 48 family disassembler
#

import instree
import disass

#######################################################################

class mcs4(disass.assy):

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

		c = self.root.find(p, adr, p.m.rd)
		assert c != None
		#print(">>>> %03x" % adr, "%02x" % p.m.rd(adr), c, "wid",c.width)
		ins.hi = ins.lo + (c.width >> 3)
		ins.mne = c.spec[0]
		ins.oper = list()
		for i in c.spec[1].split(","):
			if i == "-":
				pass
			elif i == "ladr":
				hi = c.get_field(p, adr, p.m.rd, 1, "ahi")
				lo = c.get_field(p, adr, p.m.rd, 1, "alo")
				da = (hi << 8) | lo
				ins.oper.append((da, "%s", "0x%03x" % da))
			elif i == "adr":
				hi = adr >> 8
				lo = c.get_field(p, adr, p.m.rd, 1, i)
				da = (hi << 8) | lo
				ins.oper.append((da, "%s", "0x%03x" % da))
			elif i == "rr":
				x = c.get_field(p, adr, p.m.rd, 1, i)
				x <<= 1
				ins.oper.append("rr%d" % x)
			elif i == "r":
				x = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("r%d" % x)
			elif i == "data":
				x = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("#%02x" % x)
			elif i == "d":
				x = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("#%01x" % x)
			elif i == "cc":
				x = c.get_field(p, adr, p.m.rd, 1, i)
				if x == 1:
					cc = "JNT"
				elif x == 2:
					cc = "JC"
				elif x == 4:
					cc = "JZ"
				elif x == 9:
					cc = "JT"
				elif x == 10:
					cc = "JNC"
				elif x == 12:
					cc = "JNZ"
				else:
					cc = "CC#%01x" % x
				ins.oper.append(cc)
			else:
				print("MISS", i, c)
				ins.oper.append(i)
		if ins.mne == "JCN":
			ins.flow("cond", "!" + cc, ins.hi)
			ins.flow("cond", cc, da)
		elif ins.mne == "ISZ":
			ins.flow("cond", "Z", ins.hi)
			ins.flow("cond", "NZ", da)
		elif ins.mne == "JUN":
			ins.flow("cond", "T", da)
		elif ins.mne == "JMS":
			ins.flow("call", "T", da)
		elif ins.mne == "BBL":
			ins.flow("ret", "T", None)
		
