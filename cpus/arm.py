#!/usr/local/bin/python
#

from __future__ import print_function

import const
import disass
import instree

cond_code = (
	"EQ", "NE", "CS", "CC", "MI", "PL", "VS", "VC",
	"HI", "LS", "GE", "LT", "GT", "LE", "T",  "F"
)

class arm(disass.assy):
	"""
	"""

	def __init__(self, p, name = "arm", arch="cortex-m3"):
		disass.assy.__init__(self, p, name)
		self.thumb_root = instree.instree(
		    width=16,
		    filename =  __file__[:-3] + "_thumb_instructions.txt"
		)
		self.thumb_root.load (__file__[:-3] + "_thumb2_instructions.txt")
		self.thumb_root.load (__file__[:-3] + "_thumb3_instructions.txt")
		self.arch = arch
		self.thumb_root.print()

	def disass(self, adr, priv=None):
		a0 = adr & ~1
		ins = disass.assy.disass(self, a0, priv)
		if adr & 1:
			ins.thumb = True
		else:
			ins.thumb = False
		return ins

	def do_disass(self, adr, ins):
		#assert ins.lo == adr
		assert ins.status == "prospective"

		if ins.thumb:
			self.do_thumb(adr, ins)
		else:
			self.do_thumb(adr, ins)
			#assert ins.thumb

	def do_arm(self, adr, ins):
		return


	def thumb_field(self, p, c, adr, fld):
		return c.get_field(p, adr, p.m.l16, 2, fld)
		
	def do_thumb(self, adr, ins):

		p = self.p	
		iw = p.m.b16(adr)
		# XXX: below needed ?
		ins.oper = list()
		try:
			c = self.thumb_root.find(p, adr, p.m.l16)
		except:
			ins.mne = "???"
			ins.hi = ins.lo + 2
			return
		print("IW %08x %04x" % (adr, iw), c)

		if iw == 0:
			ins.mne = "???"
			ins.hi = ins.lo + 2
			return

		ins.mne = c.spec[0]

		na = adr + (c.width >> 3)

		for i in c.spec[1].split(","):
			if i == "simm11":
				da = self.thumb_field(p, c, adr, i)
				da = da << 1
				if da & 0x0800:
					da -= 4096
				da = da + 4 + adr
				ins.oper.append((da, "0x%08x" % da))
				ins.flow("cond", "T", da)
			elif i == "[SP+imm8l*4]":
				da = self.thumb_field(p, c, adr, "imm8l")
				da = da << 2
				ins.oper.append(("[SP,#0x%x]" % da))
			elif i == "[PC+imm8l*4]":
				da = self.thumb_field(p, c, adr, "imm8l")
				da = da << 2
				da += (adr & ~3) + 4
				ins.oper.append((da, "0x%08x" % da))
				const.w32(p,da)
			elif i == "[Rn+Rm]":
				rn = self.thumb_field(p, c, adr, "Rn")
				rm = self.thumb_field(p, c, adr, "Rm")
				ins.oper.append("[R%d,R%d]" % (rn, rm))
			elif i == "[Rn+imm5]":
				da = self.thumb_field(p, c, adr, "imm5")
				rn = self.thumb_field(p, c, adr, "Rn")
				ins.oper.append("[R%d,#0x%x]" % (rn, da))
			elif i == "[Rn+imm5w*2]":
				da = self.thumb_field(p, c, adr, "imm5w")
				rn = self.thumb_field(p, c, adr, "Rn")
				ins.oper.append("[R%d,#0x%x]" % (rn, da << 1))
			elif i == "[Rn+imm5l*4]":
				da = self.thumb_field(p, c, adr, "imm5l")
				rn = self.thumb_field(p, c, adr, "Rn")
				ins.oper.append("[R%d,#0x%x]" % (rn, da << 2))
			elif i == "Rd" or i == "Rm" or i == "Rn":
				da = self.thumb_field(p, c, adr, i)
				ins.oper.append("R%d" % da)
			elif i == "RdH":
				r = self.thumb_field(p, c, adr, "Rd")
				if self.thumb_field(p, c, adr, "H"):
					r += 8
				ins.oper.append("R%d" % r)
			elif i == "Rmh":
				r = self.thumb_field(p, c, adr, "Rm")
				if self.thumb_field(p, c, adr, "h"):
					r += 8
				ins.oper.append("R%d" % r)
				ins.flow("cond", "T", None)
			elif i == "imm7l" or i == "imm8l":
				da = self.thumb_field(p, c, adr, i)
				ins.oper.append("#0x%x" % (da << 2))
			elif i == "imm8" or i == "imm5" or i == "imm3":
				da = self.thumb_field(p, c, adr, i)
				ins.oper.append("#0x%x" % da)
			elif i == "simm8":
				da = self.thumb_field(p, c, adr, i)
				if da & 0x80:
					da -= 256
				da = da << 1
				da += adr + 4
				ins.oper.append((da, "0x%08x" % da))
			elif i == "cond":
				cc = self.thumb_field(p, c, adr, i)
				da = ins.oper[-1][0]
				if ins.mne == "B":
					ins.flow("cond", cond_code[cc], da)
					if cc != 14:
						ins.flow("cond", cond_code[cc ^ 1], adr + 2)
				ins.mne += cond_code[cc]
			elif i == "bl_tgt":
				da = self.thumb_field(p, c, adr, "off11_a")
				da = da << 12
				if da & 0x400000:
					da |= 0xff800000
				da += (adr & ~3) + 4
				db = self.thumb_field(p, c, adr, "off11_b")
				da += db << 1
				da = da & 0xffffffff
				ins.oper.append((da, "0x%08x" % da))
				if ins.mne == "BL":
					ins.flow("call", "T", da)
			elif i == "regs":
				l = list()
				r = self.thumb_field(p, c, adr, i)
				for i in range(0,8):
					if r & (1 << i):
						l.append("R%d" % i)
				r = self.thumb_field(p, c, adr, "R")
				if r:
					l.append("LR")
				ins.oper.append("{" + ",".join(l) + "}")
			elif i == "SP":
				ins.oper.append(i)
			else:
				try:
					arg = self.thumb_field(p,c, adr, i)
				except:
					arg = None
				ins.oper.append(i)
				print(">>>", i, arg)
				ins.flow("ret", "T", None)

		ins.hi = na
		print("==", ins, ins.mne, ins.oper)
