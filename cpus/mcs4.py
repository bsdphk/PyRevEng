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
				reg8 = c.get_field(p, adr, p.m.rd, 1, i)
				reg8 <<= 1
				ins.oper.append("rr%d" % reg8)
			elif i == "r":
				reg = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("r%d" % reg)
			elif i == "data":
				d8 = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("#0x%02x" % d8)
			elif i == "d":
				d4 = c.get_field(p, adr, p.m.rd, 1, i)
				ins.oper.append("#0x%01x" % d4)
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
			elif i == "(rr0)":
				ins.oper.append(i)
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

		#############
		# PSEUDO CODE

		if ins.mne == "ADD":
			ins.pseudo = (
				("add",	("ra", ins.oper[0]),	"tmp0"),
				("add", ("tmp0", "rc"),		"tmp1"),
				("mov", ("tmp1",),		"ra"),
				(">>",	("tmp1", 4),		"rc"),
			)
		elif ins.mne == "ADM":
			ins.pseudo = (
				("or",  ("rdcl", "rsrc"),	"tmp0"),
				("ldm", ("tmp0", "RAM"),	"tmp1"),
				("add", ("tmp1", "ra"),		"tmp0"),
				("add", ("tmp0", "rc"),		"tmp1"),
				("mov", ("tmp1",),		"ra"),
				(">>",	("tmp1", 4),		"rc"),
			)
		elif ins.mne == "BBL":
			ins.pseudo = (
				("mov", (d4,),			"ra"),
				("ret", (),			None),
			)
		elif ins.mne == "CLB":
			ins.pseudo = (
				("mov", (0,),			"ra"),
				("mov", (0,),			"rc"),
			)
		elif ins.mne == "CLC":
			ins.pseudo = (
				("mov", (0,),			"rc"),
			)
		elif ins.mne == "CMA":
			ins.pseudo = (
				("xor", ("ra", 0xf),		"tmp0"),
				("mov", ("tmp0",),		"ra"),
			)
		elif ins.mne == "CMC":
			ins.pseudo = (
				("xor", (0x1, "rc"),		"tmp0"),
				("mov", ("tmp0",),		"rc"),
			)
		elif ins.mne == "DAA":
			ins.pseudo = (
				("mcs4::daa", ("ra", "rc"),	"tmp0"),
				("mov", ("tmp0",),		"ra"),
				(">>",	("tmp0", 4),		"rc"),
			)
		elif ins.mne == "DAC":
			ins.pseudo = (
				("add", ("ra", 0xf),		"tmp0"),
				("mov", ("tmp0",),		"ra"),
				(">>",  ("tmp0", 4),		"rc"),
			)
		elif ins.mne == "DCL":
			ins.pseudo = (
				("<<", ("ra", 8), 		"rdcl"),
			)
		elif ins.mne == "FIN":
			ins.pseudo = (
				("or",	(ins.hi & 0xf00, "r1"),	"tmp0"),
				("<<",	("r0", 4),		"tmp1"),
				("or",	("tmp1", "tmp0"),	"tmp2"),
				("ldm", ("tmp2", "ROM"),	"tmp1"),
				("mov", ("tmp1",),	"r%d" % (reg8 + 1)),
				(">>",  ("tmp1", 4),	"r%d" % reg8),
			)
		elif ins.mne == "FIM":
			ins.pseudo = (
				("mov", (d8>>4,),	"r%d" % reg8),
				("mov", (d8 & 0xf,),	"r%d" % (reg8+1)),
			)
		elif ins.mne == "IAC":
			ins.pseudo = (
				("add", ("ra", 1), 		"tmp0"),
				("mov", ("tmp0",),		"ra"),
				(">>", ("tmp0", 4),		"rc"),
			)
		elif ins.mne == "INC":
			ins.pseudo = (
				("add", (1, ins.oper[0]),	"tmp0"),
				("mov", ("tmp0",),		ins.oper[0]),
			)
		elif ins.mne == "ISZ":
			ins.pseudo = (
				("add", (1, ins.oper[0]),	"tmp0"),
				("mov", ("tmp0",),		ins.oper[0]),
				# xxx: cond-jump
			)
		elif ins.mne == "JCN":
			ins.pseudo = (
				("xxx", ins.oper,		None),
			)
		elif ins.mne == "JIN":
			ins.pseudo = (
				("xxx", ins.oper[0],		None),
			)
		elif ins.mne == "JMS":
			ins.pseudo = (
				("invoke", ins.oper[0],		None),
			)
		elif ins.mne == "JUN":
			ins.pseudo = (
				("jump", ins.oper[0],		None),
			)
		elif ins.mne == "KBP":
			ins.pseudo = (
				("mcs4::kbp", ("ra",),		"tmp0"),
				("mov", ("tmp0",),		"ra"),
			)
		elif ins.mne == "LD":
			ins.pseudo = (
				("mov", (ins.oper[0],),		"ra"),
			)
		elif ins.mne == "LDM":
			ins.pseudo = (
				("mov", (d4,),			"ra"),
			)
		elif ins.mne == "NOP":
			ins.pseudo = (
				("nop", (),			None),
			)
		elif ins.mne == "RAL":
			ins.pseudo = (
				("<<",	("ra", 1),		"tmp0"),
				("or",	("tmp0", "rc"),		"tmp1"),
				("mov", ("tmp1",),		"ra"),
				(">>",	("tmp1", 4),		"rc"),
			)
		elif ins.mne == "RAR":
			ins.pseudo = (
				("<<",	("rc", 3),		"tmp0"),
				("mov", ("ra",),		"rc"),
				(">>",	("ra", 1),		"tmp1"),
				("or",	("tmp0", "tmp1"),	"ra"),
			)
		elif ins.mne in ("RD0", "RD1", "RD2", "RD3"):
			ins.pseudo = (
				("or",	("rdcl", "rsrc"),	"tmp0"),
				("and", ("tmp0", 0x7f0),	"tmp1"),
				("ldm", ("tmp1", int(ins.mne[-1]),
				    "RAMSTATUS"),		"ra"),
			)
		elif ins.mne == "RDM":
			ins.pseudo = (
				("or",	("rdcl", "rsrc"),	"tmp0"),
				("ldm", ("tmp0", "RAM"),	"ra"),
			)
		elif ins.mne == "RDR":
			ins.pseudo = (
				("and", ("rsrc", 0xf0),		"tmp0"),
				("ldm", ("tmp0", "ROMPORT"),	"ra"),
			)
		elif ins.mne == "SBM":
			ins.pseudo = (
				("or",	("rdcl", "rsrc"),	"tmp0"),
				("ldm", ("tmp0", "RAM"),	"tmp1"),
				("xor", ("tmp1", 0xf),		"tmp0"),
				("add", ("tmp0", "ra"),		"tmp1"),
				("xor", ("rc", 0x1),		"tmp0"),
				("add", ("tmp0", "tmp1"),	"tmp2"),
				("mov", ("tmp2",),		"ra"),
				(">>",	("tmp2", 4),		"rc"),
			)
		elif ins.mne == "SRC":
			ins.pseudo = (
				("<<", ("r%d" % reg8, 4),	"tmp0"),
				("or", ("r%d" % (reg8+1), "tmp0"), "rsrc"),
			)
		elif ins.mne == "STC":
			ins.pseudo = (
				("mov", (1,),			"tc"),
			)
		elif ins.mne == "SUB":
			ins.pseudo = (
				("xor", (ins.oper[0], 0xf),	"tmp0"),
				("add", ("tmp0", "ra"),		"tmp1"),
				("xor", ("rc", 1),		"tmp0"),
				("add", ("tmp0", "tmp1"),	"tmp2"),
				("mov", ("tmp2",),		"ra"),
				(">>",  ("tmp2", 4),		"rc"),
			)
		elif ins.mne == "TCC":
			ins.pseudo = (
				("mov", ("rc",),		"ra"),
				("mov", (0,),			"rc"),
			)
		elif ins.mne == "TCS":
			ins.pseudo = (
				("add", ("rc", 9),		"ra"),
				("mov", (0,),			"rc"),
			)
		elif ins.mne == "WMP":
			ins.pseudo = (
				("or",	("rdcl", "rsrc"),	"tmp0"),
				("and", ("tmp0", 0x7c0),	"tmp1"),
				("stm", ("ra", "tmp1", "RAMPORT"), True),
			)
		elif ins.mne in ("WR0", "WR1", "WR2", "WR3"):
			ins.pseudo = (
				("or",	("rdcl", "rsrc"),	"tmp0"),
				("and", ("tmp0", 0x7f0),	"tmp1"),
				("stm", ("ra", "tmp1", int(ins.mne[-1]),
				    "RAMSTATUS"), True),
			)
		elif ins.mne == "WRM":
			ins.pseudo = (
				("or", ("rdcl", "rsrc"),	"tmp0"),
				("stm", ("ra", "tmp0", "RAM"),	True),
			)
		elif ins.mne == "WRR":
			ins.pseudo = (
				("and", ("rsrc", 0xf0),		"tmp0"),
				("stm", ("ra", "tmp0", "ROMPORT"), True),
			)
		elif ins.mne == "XCH":
			ins.pseudo = (
				("mov", ("ra",),		"tmp0"),
				("mov", (ins.oper[0],),		"ra"),
				("mov", ("tmp0",),		ins.oper[0]),
			)
		else:
			print("XXX: Missing pseudo", ins.mne)
		for i in ins.pseudo:
			for j in i[1]:
			    if type(j) == str and i[2] == j:
				    print("XXX", i, ins.mne, ins.oper)
		
