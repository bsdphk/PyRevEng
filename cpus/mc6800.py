#!/usr/local/bin/python
#
# Motorola 6800 CPU disassembler
#

from __future__ import print_function

import const
import disass

inscode = (
	"0-???", "1 NOP", "0-???", "0-???", "0-???", "0-???", "1 TAP", "1 TPA",
	"1 INX", "1 DEX", "1 CLV", "1 SEV", "1 CLC", "1 SLC", "1 CLI", "1 SEI",

	"1 SBA", "1 CBA", "0-???", "0-???", "0-???", "0-???", "1 TAB", "1 TBA",
	"0-???", "1 DAA", "0-???", "1 ABA", "0-???", "0-???", "0-???", "0-???",

	"2rBRA", "0-???", "2rBHI", "2rBLS", "2rBCC", "2rBCS", "2rBNE", "2rBEQ",
	"2rBVC", "2rBVS", "2rBPL", "2rBMI", "2rBGE", "2rBLT", "2rBGT", "2rBLE",

	"1 TSX", "1 INS", "1 PULA","1 PULB","1 DES", "1 TXS", "1 PSHA","1 PSHB",
	"0-???", "1_RTS", "0-???", "1_RTI", "0-???", "0-???", "1 WAI", "1wSWI",


	"1 NEGA","0-???", "0-???", "1 COMA","1 LSRA","0-???", "1 RORA","1 ASLA",
	"1 ASLA","1 ROLA","1 DECA","0-???", "1 INCA","1 TSTA","0-???", "1 CLRA",

	"1 NEGB","0-???", "0-???", "1 COMB","1 LSRB","0-???", "1 RORB","1 ASRB",
	"1 ASLB","1 ROLB","1 DECB","0-???", "1 INCB","1 TSTB","0-???", "1 CLRB",

	"2xNEG", "0-???", "0-???", "2xCOM", "2xLSR", "0-???", "2xROR", "2xASR",
	"2xASL", "2xROL", "2xDEC", "0-???", "2xINC", "2xTST", "2XJMP", "2xCLR",

	"3eNEG", "0-???", "0-???", "3eCOM", "3eLSR", "0-???", "3eROR", "3eASR",
	"3eASL", "3eROL", "3eDEC", "0-???", "3eINC", "3eTST", "3jJMP", "3eCLR",


	"2iSUBA","2iCMPA","2iSBCA","0-???", "2iANDA","2iBITA","2iLDAA","0-???",
	"2iEORA","2iADCA","2iORAA","2iADDA","3iCPX", "2RBSR", "3iLDS", "0-???",

	"2dSUBA","2dCMPA","2dSBCA","0-???", "2dANDA","2dBITA","2dLDAA","2dSTAA",
	"2dEORA","2dADCA","2dORAA","2dADDA","2dCPX", "0-???", "2dLDS", "2dSTS",

	"2xSUBA","2xCMPA","2xSBCA","0-???", "2xANDA","2xBITA","2xLDAA","2xSTAA",
	"2xEORA","2xADCA","2xORAA","2xADDA","2xCPX", "2XJSR", "2xLDS", "2xSTS",

	"3eSUBA","3eCMPA","2eSBCA","0-???", "3eANDA","3eBITA","3eLDAA","3eSTAA",
	"3eEORA","3eADCA","3eORAA","3eADDA","3eCPX", "3sJSR", "3eLDS", "3eSTS",


	"2iSUBB","2iCMPB","2iSBCB","0-???", "2iANDB","2iBITB","2iLDAB","0-???",
	"2iEORB","2iADCB","2iORAB","2iADDB","0-???", "0-???", "3iLDX", "0-???",

	"2dSUBB","2dCMPB","2dSBCB","0-???", "2dANDB","2dBITB","2dLDAB","2dSTAB",
	"2dEORB","2dADCB","2dORAB","2dADDB","0-???", "0-???", "2dLDX", "2dSTX",

	"2xSUBB","2xCMPB","2xSBCB","0-???", "2xANDB","2xBITB","2xLDAB","2xSTAB",
	"2xEORB","2xADCB","2xORAB","2xADDB","0-???", "0-???", "2xLDX", "2xSTX",

	"3eSUBB","3eSTXB","3eSBCB","3eANDB","3eBITB","3eLDAB","3eLDAB","3eSTAB",
	"3eEORB","3eADCB","3eORAB","3eADDB","0-???", "0-???", "3eLDX", "3eSTX",
)

class mc6800(disass.assy):
	"""Motorola MC6800 Disassembler
	"""

	def __init__(self, p, name = "mc6800"):
		disass.assy.__init__(self, p, name)
		assert inscode[0x80] == "2iSUBA"
		assert inscode[0xc0] == "2iSUBB"
		assert len(inscode) == 256

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		p = self.p

		iw = p.m.rd(adr)

		c = inscode[iw]
		l = int(c[0])
		if l == 0:
			raise disass.DisassError("no instruction")

		ins.hi = adr + l
		if False:
			try:
				x = p.t.add(adr, adr + l, "ins")
				x.render = self.render
			except:
				print ("FAIL @ 0x%04x" % adr)
				return
		
		ins.mne = c[2:]

		if c[1] == "i" and l == 2:
			ins.oper = ("#0x%02x" % p.m.rd(adr + 1),)
		elif c[1] == "i" and l == 3:
			aa = p.m.b16(adr + 1)
			ins.oper = ("#0x%04x" % aa,)
			try:
				p.m.rd(aa)
				#XXX ins.ea = (aa,)
			except:
				pass
		elif c[1] == "x" and l == 2:
			ins.oper = ("0x%02x" % p.m.rd(adr + 1),"X")
		elif c[1] == "d":
			ins.oper = ("0x%02x" % p.m.rd(adr + 1),)
			#XXX ins.ea = (p.m.rd(adr + 1),)
		elif c[1] == "e":
			aa = p.m.b16(adr + 1)
			ins.oper = ("0x%04x" % aa,)
			#XXX ins.ea = (aa,)
		elif c[1] == "s":
			da = p.m.b16(adr + 1)
			ins.oper.append((da, "%s"))
			ins.flow("call", "T", da)
		elif c[1] == "R":
			da = adr + 2 + p.m.s8(adr + 1)
			ins.oper.append((da, "%s"))
			ins.flow("call", "T", da)
		elif c[1] == "r":
			da = adr + 2 + p.m.s8(adr + 1)
			ins.oper.append((da, "%s"))
			if iw & 0x0f == 00:
				ins.flow("cond", "T", da)
			else:
				c2 = inscode[iw ^ 1]
				ins.flow("cond", c2[3:], adr + l)
				ins.flow("cond", c[3:], da)
		elif c[1] == "j":
			da = p.m.b16(adr + 1)
			ins.oper.append((da, "%s"))
			ins.flow("cond", "T", da)
		elif c[1] == "X":
			ins.oper = ("0x%02x" % p.m.rd(adr + 1),"X")
			if ins.mne == "JSR":
				ins.flow("call", "T", None)
			else:
				ins.flow("cond", "T", None)
		elif c[1] == "_":
			if c[2:] == "RTI":
				ins.flow("ret", "IRQ", None)
			else:
				ins.flow("ret", "T", None)
		elif c[1] == "w":
			ins.flow("call.SWI", "T", None)
		elif c[1] == " ":
			pass
		else:
			print("UNIMPL %04x: %02x %s" % (adr,iw, c))
			raise disass.DisassError("bug", c)

	def __vector(self, adr, nm):
		x = const.w16(self.p, adr)
		x.cmt.append("Vector: " + nm)
		w = self.p.m.w16(adr)
		x.a['flow'] = (("cond", "T", w),)
		self.disass(w)
		self.p.setlabel(w, nm + "_VECTOR")

	def vectors(self, adr = 0x10000):
		"""Instantiate the four MC6800 vectors

		adr:
			Address mapped to top of memory
		"""

		self.__vector(adr - 2, "RST")
		self.__vector(adr - 4, "NMI")
		self.__vector(adr - 6, "SWI")
		self.__vector(adr - 8, "IRQ")
		x = self.p.t.add(adr - 8, adr, "tbl")
		x.blockcmt += "\n-\nMC6800 Vector Table\n\n"
