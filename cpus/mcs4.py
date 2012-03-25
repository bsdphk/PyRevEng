#!/usr/local/bin/python
#
# Intel MCS 48 family disassembler
#

import instree
import disass

import pseudo

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
				pseudo.add(("ra", ins.oper[0]),	"tmp0"),
				pseudo.add(("tmp0", "rc"),		"tmp1"),
				pseudo.mov(("tmp1",),		"ra"),
				pseudo.rsh(("tmp1", 4),		"rc"),
			)
		elif ins.mne == "ADM":
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.ldm(("tmp0", "RAM"),	"tmp1"),
				pseudo.add(("tmp1", "ra"),		"tmp0"),
				pseudo.add(("tmp0", "rc"),		"tmp1"),
				pseudo.mov(("tmp1",),		"ra"),
				pseudo.rsh(("tmp1", 4),		"rc"),
			)
		elif ins.mne == "BBL":
			ins.pseudo = (
				pseudo.mov((d4,),			"ra"),
				pseudo.ret((),			None),
			)
		elif ins.mne == "CLB":
			ins.pseudo = (
				pseudo.mov((0,),			"ra"),
				pseudo.mov((0,),			"rc"),
			)
		elif ins.mne == "CLC":
			ins.pseudo = (
				pseudo.mov((0,),			"rc"),
			)
		elif ins.mne == "CMA":
			ins.pseudo = (
				pseudo.xor(("ra", 0xf),		"tmp0"),
				pseudo.mov(("tmp0",),		"ra"),
			)
		elif ins.mne == "CMC":
			ins.pseudo = (
				pseudo.xor((0x1, "rc"),		"tmp0"),
				pseudo.mov(("tmp0",),		"rc"),
			)
		elif ins.mne == "DAA":
			ins.pseudo = (
				pseudo.xxx(("ra", "rc"), "tmp0"),
				# ("mcs4::daa", ("ra", "rc"),	"tmp0"),
				pseudo.mov(("tmp0",),		"ra"),
				pseudo.rsh(("tmp0", 4),		"rc"),
			)
		elif ins.mne == "DAC":
			ins.pseudo = (
				pseudo.add(("ra", 0xf),		"tmp0"),
				pseudo.mov(("tmp0",),		"ra"),
				pseudo.rsh(("tmp0", 4),		"rc"),
			)
		elif ins.mne == "DCL":
			ins.pseudo = (
				pseudo.lsh(("ra", 8), 		"rdcl"),
			)
		elif ins.mne == "FIN":
			ins.pseudo = (
				pseudo.lor((ins.hi & 0xf00, "r1"),	"tmp0"),
				pseudo.lsh(("r0", 4),		"tmp1"),
				pseudo.lor(("tmp1", "tmp0"),	"tmp2"),
				pseudo.ldm(("tmp2", "ROM"),	"tmp1"),
				pseudo.mov(("tmp1",),	"r%d" % (reg8 + 1)),
				pseudo.rsh(("tmp1", 4),	"r%d" % reg8),
			)
		elif ins.mne == "FIM":
			ins.pseudo = (
				pseudo.mov((d8>>4,),	"r%d" % reg8),
				pseudo.mov((d8 & 0xf,),	"r%d" % (reg8+1)),
			)
		elif ins.mne == "IAC":
			ins.pseudo = (
				pseudo.add(("ra", 1), 		"tmp0"),
				pseudo.mov(("tmp0",),		"ra"),
				pseudo.rsh(("tmp0", 4),		"rc"),
			)
		elif ins.mne == "INC":
			ins.pseudo = (
				pseudo.add((1, ins.oper[0]),	"tmp0"),
				pseudo.mov(("tmp0",),		ins.oper[0]),
			)
		elif ins.mne == "ISZ":
			ins.pseudo = (
				pseudo.add((1, ins.oper[0]),	"tmp0"),
				pseudo.mov(("tmp0",),		ins.oper[0]),
				pseudo.xxx(),
			)
		elif ins.mne == "JCN":
			ins.pseudo = (
				pseudo.xxx(),
			)
		elif ins.mne == "JIN":
			ins.pseudo = (
				pseudo.xxx(),
			)
		elif ins.mne == "JMS":
			ins.pseudo = (
				pseudo.xxx(),
			)
		elif ins.mne == "JUN":
			ins.pseudo = (
				pseudo.xxx(),
			)
		elif ins.mne == "KBP":
			ins.pseudo = (
				pseudo.xxx(("ra",), "tmp0"),
				# ("mcs4::kbp", ("ra",),		"tmp0"),
				pseudo.mov(("tmp0",),		"ra"),
			)
		elif ins.mne == "LD":
			ins.pseudo = (
				pseudo.mov((ins.oper[0],), "ra"),
			)
		elif ins.mne == "LDM":
			ins.pseudo = (
				pseudo.mov((d4,),			"ra"),
			)
		elif ins.mne == "NOP":
			ins.pseudo = (
				pseudo.nop(),
			)
		elif ins.mne == "RAL":
			ins.pseudo = (
				pseudo.lsh(("ra", 1),		"tmp0"),
				pseudo.lor(("tmp0", "rc"),		"tmp1"),
				pseudo.mov(("tmp1",),		"ra"),
				pseudo.rsh(("tmp1", 4),		"rc"),
			)
		elif ins.mne == "RAR":
			ins.pseudo = (
				pseudo.lsh(("rc", 3),		"tmp0"),
				pseudo.mov(("ra",),		"rc"),
				pseudo.rsh(("ra", 1),		"tmp1"),
				pseudo.lor(("tmp0", "tmp1"),	"ra"),
			)
		elif ins.mne in ("RD0", "RD1", "RD2", "RD3"):
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.land(("tmp0", 0x7f0),	"tmp1"),
				pseudo.ldm(("tmp1", int(ins.mne[-1]),
				    "RAMSTATUS"),		"ra"),
			)
		elif ins.mne == "RDM":
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.ldm(("tmp0", "RAM"),	"ra"),
			)
		elif ins.mne == "RDR":
			ins.pseudo = (
				pseudo.land(("rsrc", 0xf0),		"tmp0"),
				pseudo.ldm(("tmp0", "ROMPORT"),	"ra"),
			)
		elif ins.mne == "SBM":
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.ldm(("tmp0", "RAM"),	"tmp1"),
				pseudo.xor(("tmp1", 0xf),		"tmp0"),
				pseudo.add(("tmp0", "ra"),		"tmp1"),
				pseudo.xor(("rc", 0x1),		"tmp0"),
				pseudo.add(("tmp0", "tmp1"),	"tmp2"),
				pseudo.mov(("tmp2",),		"ra"),
				pseudo.rsh(("tmp2", 4),		"rc"),
			)
		elif ins.mne == "SRC":
			ins.pseudo = (
				pseudo.lsh(("r%d" % reg8, 4),	"tmp0"),
				pseudo.lor(("r%d" % (reg8+1), "tmp0"), "rsrc"),
			)
		elif ins.mne == "STC":
			ins.pseudo = (
				pseudo.mov((1,),			"tc"),
			)
		elif ins.mne == "SUB":
			ins.pseudo = (
				pseudo.xor((ins.oper[0], 0xf),	"tmp0"),
				pseudo.add(("tmp0", "ra"), "tmp1"),
				pseudo.xor(("rc", 1),		"tmp0"),
				pseudo.add(("tmp0", "tmp1"),	"tmp2"),
				pseudo.mov(("tmp2",),		"ra"),
				pseudo.rsh(("tmp2", 4),		"rc"),
			)
		elif ins.mne == "TCC":
			ins.pseudo = (
				pseudo.mov(("rc",),		"ra"),
				pseudo.mov((0,),			"rc"),
			)
		elif ins.mne == "TCS":
			ins.pseudo = (
				pseudo.add(("rc", 9),		"ra"),
				pseudo.mov((0,),			"rc"),
			)
		elif ins.mne == "WMP":
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.land(("tmp0", 0x7c0),	"tmp1"),
				pseudo.stm(("ra", "tmp1", "RAMPORT"), True),
			)
		elif ins.mne in ("WR0", "WR1", "WR2", "WR3"):
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.land(("tmp0", 0x7f0),	"tmp1"),
				pseudo.stm(("ra", "tmp1", int(ins.mne[-1]),
				    "RAMSTATUS"), True),
			)
		elif ins.mne == "WRM":
			ins.pseudo = (
				pseudo.lor(("rdcl", "rsrc"),	"tmp0"),
				pseudo.stm(("ra", "tmp0", "RAM"),	True),
			)
		elif ins.mne == "WRR":
			ins.pseudo = (
				pseudo.land(("rsrc", 0xf0),		"tmp0"),
				pseudo.stm(("ra", "tmp0", "ROMPORT"), True),
			)
		elif ins.mne == "XCH":
			ins.pseudo = (
				pseudo.mov(("ra",),		"tmp0"),
				pseudo.mov((ins.oper[0],),		"ra"),
				pseudo.mov(("tmp0",),		ins.oper[0]),
			)
		else:
			print("XXX: Missing pseudo", ins.mne)
		if False:
			for i in ins.pseudo:
				for j in i[1]:
				    if type(j) == str and i[2] == j:
					    print("XXX", i, ins.mne, ins.oper)
		
