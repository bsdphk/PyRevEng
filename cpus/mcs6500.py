#!/usr/local/bin/python
#
# MOS Technology 650x disassembler
#

from __future__ import print_function

import const
import disass

inscode = (
#	0	1	2	3	4	5	6	7	8	9	a	b	c	d	e	f
	"",	"nORA",	"",	"",	"",	"zORA",	"zASL",	"",	"_PHP",	"iORA",	"AASL",	"",	"",	"aORA",	"aASL",	"",
	"rBPL",	"mORA",	"",	"",	"",	"XORA",	"XASL",	"",	"_CLC",	"yORA",	"",	"",	"",	"xORA",	"xASL",	"",
	"",	"nAND",	"",	"",	"zBIT",	"zAND",	"zROL",	"",	"_PLP",	"iAND",	"AROL",	"",	"aBIT",	"aAND",	"aROL",	"",
	"rBMI",	"mAND",	"",	"",	"",	"XAND",	"XROL",	"",	"_SEC",	"",	"",	"",	"",	"xAND",	"xROL",	"",

	"",	"nEOR",	"",	"",	"",	"zEOR",	"zLSR",	"",	"_PHA",	"iEOR",	"ALSR",	"",	"",	"aEOR",	"aLSR",	"",
	"rBVC",	"mEOR",	"",	"",	"",	"XEOR",	"XLSR",	"",	"_CLI",	"yEOR",	"",	"",	"",	"xEOR",	"xLSR",	"",
	"",	"nADC",	"",	"",	"",	"zADC",	"zROR",	"",	"_PLA",	"iADC",	"AROR",	"",	"",	"aADC",	"aROR",	"",
	"rBVS",	"mADC",	"",	"",	"",	"XADC",	"XROR",	"",	"_SEI",	"yADC",	"",	"",	"",	"xADC",	"xROR",	"",

	"",	"nSTA",	"",	"",	"zSTY",	"zSTA",	"zSTX",	"",	"_DEY",	"",	"_TXA",	"",	"aSTY",	"aSTA",	"aSTX",	"",
	"rBCC",	"mSTA",	"",	"",	"XSTY",	"XSTA",	"XSTY",	"",	"_TYA",	"ySTA",	"_TXS",	"",	"",	"xSTA",	"",	"",
	"iLDY",	"nLDA",	"iLDX",	"",	"zLDY",	"zLDA",	"zLDX",	"",	"_TAY",	"iLDA",	"_TAX",	"",	"aLDX",	"aLDA",	"aLDX",	"",
	"rBCS",	"mLDA",	"",	"",	"XLDY",	"XLDA",	"YLDA",	"",	"_CLV",	"yLDA",	"_TSX",	"",	"",	"xLDA",	"yLDX",	"",

	"iCPY",	"nCMP",	"",	"",	"zCPY",	"zCMP",	"zDEC",	"",	"_INY",	"iCMP",	"_DEX",	"",	"aCPY",	"aCMP",	"aDEC",	"",
	"rBNE",	"mCMP",	"",	"",	"",	"XCMP",	"XDEC",	"",	"_CLD",	"yCMP",	"",	"",	"",	"xCMP",	"xDEC",	"",
	"iCPX",	"nSBC",	"",	"",	"zCPX",	"zSBC",	"zINC",	"",	"_INX",	"iSBC",	"_NOP",	"",	"aCPX",	"aSBC",	"aINC",	"",
	"rBEQ",	"mSBC",	"",	"",	"",	"XSBC",	"XINC",	"",	"_SED",	"ySBC",	"",	"",	"",	"xSBC",	"xINC",	"",
)

class mcs6502(disass.assy):
	"""
	"""

	def __init__(self, p, name = "mcs6502"):
		disass.assy.__init__(self, p, name)
		assert len(inscode) == 256

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		p = self.p

		try:
			iw = p.m.rd(adr)
		except:
			print("FETCH failed:", adr)
			ins.fail("no mem")
			return

		ic = inscode[iw]
		#print("%02x " % iw, ic)
		if ic == "":
			ic = "-"
		if ic[0] == "z":
			# Page Zero address
			ins.mne = ic[1:]
			ins.oper.append("%02x" % p.m.rd(adr + 1))
			ins.hi = ins.lo + 2
		elif ic[0] == "X":
			# PZ,X
			da = p.m.rd(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("%02x" % da)
			ins.oper.append("X")
			ins.hi = ins.lo + 2
		elif ic[0] == "Y":
			# PZ,Y
			da = p.m.rd(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("%02x" % da)
			ins.oper.append("Y")
			ins.hi = ins.lo + 2
		elif ic[0] == "i":
			# Immediate
			ins.mne = ic[1:]
			ins.oper.append("#%02x" % p.m.rd(adr + 1))
			ins.hi = ins.lo + 2
		elif ic[0] == "a":
			# Absolute
			da = p.m.l16(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("%04x" % da)
			ins.hi = ins.lo + 3
		elif ic[0] == "x":
			# Absolute,X
			da = p.m.l16(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("%04x" % da)
			ins.oper.append("X")
			ins.hi = ins.lo + 3
		elif ic[0] == "y":
			# Absolute,Y
			da = p.m.l16(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("%04x" % da)
			ins.oper.append("Y")
			ins.hi = ins.lo + 3
		elif ic[0] == "n":
			# (Ind,X)
			da = p.m.rd(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("(%02x,X)" % da)
			ins.hi = ins.lo + 2
		elif ic[0] == "m":
			# (Ind,Y)
			da = p.m.rd(adr + 1)
			ins.mne = ic[1:]
			ins.oper.append("(%02x,Y)" % da)
			ins.hi = ins.lo + 2
		elif ic[0] == "r":
			# Relative
			ins.mne = ic[1:]
			da = ins.lo + 2 + p.m.s8(adr + 1)
			ins.oper.append((da, "%s", "%04x" % da))
			ins.flow("cond", ic[2:], da)
			if da == adr and False:
				ins.mne += "LOOP"
			else:
				ins.flow("cond", "N" + ic[2:], adr + 2)
			ins.hi = ins.lo + 2
		elif ic[0] == "A":
			# Acc
			ins.mne = ic[1:]
			ins.oper.append("A")
		elif ic[0] == "_":
			# Implied
			ins.mne = ic[1:]
		elif iw == 0x00:
			ins.mne = "BRK"
			ins.flow("cond", "IRQ", None)
		elif iw == 0x20:
			ins.mne = "JSR"
			da = p.m.l16(adr + 1)
			ins.flow("call", "T", da)
			ins.oper.append((da, "%s", "%04x" % da))
			ins.hi = ins.lo + 3
		elif iw == 0x40:
			ins.mne = "RTI"
			ins.flow("ret", "IRQ", None)
		elif iw == 0x6c:
			# JMP (ind)
			ins.mne = "JMP"
			da = p.m.l16(adr + 1)
			ins.oper.append((da, "(%s)", "(%04x)" % da))
			ins.flow("cond", "T", None)
			ins.hi = ins.lo + 3
		elif iw == 0x4c:
			# JMP abs
			ins.mne = "JMP"
			da = p.m.l16(adr + 1)
			ins.oper.append((da, "%s", "%04x" % da))
			ins.flow("cond", "T", da)
			ins.hi = ins.lo + 3
		elif iw == 0x60:
			ins.mne = "RTS"
			ins.flow("ret", "T", None)
		else:
			ins.fail("NYI %02x" % iw)


