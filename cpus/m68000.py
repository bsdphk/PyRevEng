#!/usr/local/bin/python
#
# Motorola M68000 CPU disassembler
#

from __future__ import print_function

import instree
import disass
import const

#######################################################################
def reglist_word(w, p, l):
	w = w & 0xff
	if (w == 0):
		return ""
	i = 0
	s = ""
	while (i < 8):
		if (w & (1 << i)):
			s = s + "," + p + l[i]
			j = i 
			while ((w & (1 << j))):
				j = j + 1
			if (j > i + 1):
				s = s + "-" + l[j - 1]
				i = j - 1
		i = i + 1
	return s

def reglist(w):
	r = reglist_word(w, "D", "01234567") + \
	    reglist_word(w >> 8, "A", "01234567")
	return "[" + r[1:] + "]"

def regrlist(w):
	r = reglist_word(w >> 8, "D", "76543210") + \
	    reglist_word(w, "A", "76543210")
	return "[" + r[1:] + "]"

#######################################################################

def ask_gdb(m, a):
	import subprocess

	fo = open("/tmp/_.bin", "wb")
	b = bytearray()
	for i in range(16):
		b.append(m.rd(a + i))
	fo.write(b)
	fo.close()

	b = subprocess.check_output([
		"m68k-rtems-objdump",
		"-bbinary",
		"-D",
		"--adjust-vma=0x%x" % a,
		"-mm68k:68030",
		"/tmp/_.bin"
	])
	b=b.decode("ascii").split("\n")
	return b[7]


#######################################################################

special_registers = {
	"USP", "CCR", "SR"
}

condition_codes = (
	"T",  "F",  "HI", "LS", "CC", "CS", "NE", "EQ",
	"VC", "VS", "PL", "MI", "GE", "LT", "GT", "LE"
)

m68kvecs = {}
m68kvecs[0] = "Reset ISP"
m68kvecs[1] = "Reset PC"
m68kvecs[2] = "Bus Error"
m68kvecs[3] = "Address Error"
m68kvecs[4] = "Illegal Instruction"
m68kvecs[5] = "Zero Divide"
m68kvecs[6] = "CHK instr"
m68kvecs[7] = "TRAPV instr"
m68kvecs[8] = "Priv violation"
m68kvecs[9] = "Trace"
m68kvecs[10] = "Line 1010 Emulator"
m68kvecs[11] = "Line 1111 Emulator"
m68kvecs[12] = "Unasgn Trap 12"
m68kvecs[13] = "Coproc proto violation"
m68kvecs[14] = "Format error"
m68kvecs[15] = "Uninit Irq"
m68kvecs[24] = "Spurious Irq"
m68kvecs[25] = "Lev 1 IRQ"
m68kvecs[26] = "Lev 2 IRQ"
m68kvecs[27] = "Lev 3 IRQ"
m68kvecs[28] = "Lev 4 IRQ"
m68kvecs[29] = "Lev 5 IRQ"
m68kvecs[30] = "Lev 6 IRQ"
m68kvecs[31] = "Lev 7 IRQ"
a = 32
while (a < 48):
	m68kvecs[a] = "TRAP#%d" % (a - 32)
	a = a + 1
m68kvecs[48] = "FP Unordered"
m68kvecs[49] = "FP Inexact"
m68kvecs[50] = "FP Div Zero"
m68kvecs[51] = "FP Underflow"
m68kvecs[52] = "FP Oper Error"
m68kvecs[53] = "FP Overflow"
m68kvecs[54] = "FP Sig NaN"
m68kvecs[55] = "FP Unimpl"
m68kvecs[56] = "MMU Conf"
m68kvecs[57] = "MMU Illegal Op"
m68kvecs[58] = "MMU Access Violation"

class m68k(disass.assy):

	def __init__(self, p, name = None):
		disass.assy.__init__(self, p, name)
		self.root = instree.instree(
		   width = 16,
		   filename = __file__[:-3] + "_instructions.txt"
		)

	def load_ins(self, fn):
		self.root.load(filename = __file__[:-9] + fn)

	def vectors(self, hi, base=0x0):
		for a in range(0, hi):
			x = const.w32(self.p, base + a * 4)
			if a in m68kvecs:
				x.lcmt(m68kvecs[a])
			if a > 0:
				self.disass(self.p.m.w32(base + a * 4))

	def rdarg(self, adr, c, arg, fail_ok = False):
		x = c.get_field(self.p, adr, self.p.m.b16, 2, arg)
		if x == None and not fail_ok:
			print("NB: ", arg, "not found in", c)
		return x

	def extword(self, ins, breg, ver = True):
		adr = ins.hi
		p = self.p
		ev = p.m.b16(ins.hi)
		ins.hi += 2
		if not self.lew and (ev & 0x0700):
			return None
		ea = ""
		da = ev >> 15
		reg = (ev >> 12) & 7
		if da == 0:
			irg = "D%d" % reg
		else:
			irg = "A%d" % reg
		wl = (ev >> 11) & 1
		if wl:
			irg += ".L"
		else:
			irg += ".W"
		scale = (ev >> 9) & 3
		if scale != 0:
			irg +=  "*%d" % (1 << scale)
		if ev & 0x0100:
			bs = (ev >> 7) & 1
			Is = (ev >> 6) & 1
			bds = (ev >> 4) & 3
			iis = (ev >> 0) & 7
			if bds == 0:
				return None
			elif bds == 1:
				displ = 0
			elif bds == 2:
				displ = p.m.s16(ins.hi)
				ins.hi += 2
			else:
				displ = p.m.s32(ins.hi)
				ins.hi += 4
			if bs == 0:
				if breg != "PC":
					ea += "+" + breg
					if displ < 0:
						ea += "-0x%x" % -displ
					elif displ > 0:
						ea += "+0x%x" % displ
				else:
					ea += "+0x%x" % (adr + displ)
			else:
				ea += "+0x%x" % displ
			if Is == 0:
				ea += "+" + irg
			if iis == 0:
				pass
			elif iis == 1:
				ea = "+(" + ea[1:] + ")"
				ins.gbd = True
			else:
				ins.gbd = True
				ea += "  LEW[iis %d]" % (iis)
				ins.flow("missing_LEW", "T", None)
		else:
			displ = ev & 0xff
			if displ & 0x80:
				displ -= 256
			if breg == "PC":
				ea += "+0x%x" % (adr + displ)
				ea += "+" + irg
			else:
				ea += "+" + breg
				ea += "+" + irg
				if displ < 0:
					ea +=  "-0x%x" % -displ
				elif displ > 0:
					ea +=  "+0x%x" % displ
		return "(" + ea[1:] + ")"

	def ea(self, ins, eam, ear, wid):

		adr = ins.lo
		v = None
		if eam == 0:
			# Data Register Direct
			ea = "D%d" % ear
		elif eam == 1:
			# Address Register Direct
			ea = "A%d" % ear
		elif eam == 2:
			# Address Register Indirect
			ea = "(A%d)" % ear
		elif eam == 3:
			# Address Register Indirect with Postincrement
			ea = "(A%d)+" % ear
		elif eam == 4:
			# Adress Register Indirect with Predecrement
			ea = "-(A%d)" % ear
		elif eam == 5:
			# Adress Register Indirect with Displacement
			v = self.p.m.sb16(ins.hi)
			ins.hi += 2
			if v < 0:
				ea = "(A%d-#0x%04x)" % (ear, -v)
			else:
				ea = "(A%d+#0x%04x)" % (ear, v)
		elif eam == 6:
			# Adress Register Indirect with Index
			ea = self.extword(ins, "A%d" % ear)
			if ea == None:
				return (None, None)
		elif eam == 7 and ear == 0:
			# Absolute Short Addressing
			v = self.p.m.b16(ins.hi)
			if v & 0x8000:
				v |= 0xffff0000
			ea=(v, "%s")
			ins.hi += 2
		elif eam == 7 and ear == 1:
			# Absolute Long Adressing
			v =self.p.m.b32(ins.hi)
			ea=(v, "%s")
			ins.hi += 4
		elif eam == 7 and ear == 2:
			# Program Counter Indirect with Displacement
			v = ins.hi + self.p.m.sb16(ins.hi)
			ea=(v, "%s")
			ins.hi += 2
		elif eam == 7 and ear == 3:
			# Program Counter Indirect with Index
			ea = self.extword(ins, "PC")
			if ea == None:
				return (None, None)
		elif eam == 7 and ear == 4 and wid == 8:
			# Immediate Data (8 bit)
			ea="#0x%02x" % (self.p.m.b16(ins.hi) & 0xff)
			ins.hi += 2
		elif eam == 7 and ear == 4 and wid == 16:
			# Immediate Data (16 bit)
			v = self.p.m.b16(ins.hi)
			ea="#0x%04x" % v
			ins.hi += 2
		elif eam == 7 and ear == 4 and wid == 32:
			# Immediate Data (32 bit)
			v = self.p.m.b32(ins.hi)
			ea="#0x%08x" % v
			ins.hi += 4
		else:
			if True:
				print(("Error @%04x: %04x %04x " +
				    "EA.%d.%d w%d missing") %
				    (adr, self.p.m.b16(adr), self.p.m.b16(adr + 2),
				    eam, ear, wid))
				print("\t", self.last_c)
			return (None, None)
		#print("\team=", eam, "ear=", ear, "wid=%d" % wid, "ins.hi=%x" % ins.hi,"->", ea, v)
		return (ea, v)
		
	def check_valid_ea(self, ins, c, ver = False):
		# Figure out Effective Address
		eabit = int(c.spec[2],16)
		if eabit == 0:
			return (None, 0, 0)

		adr = ins.lo

		if eabit & 0xe080:
			if ver:
				print("Error @%04x: %04x %04x " +
				    "EAbits illegal (%04x)" %
				    (adr, self.p.m.b16(adr), self.p.m.b16(adr + 2),
				    eabit))
				print("\t", c)
			return (False, None, None)

		eam = self.rdarg(adr, c, "eam")
		ear = self.rdarg(adr, c, "ear")

		if eam == 7 and (eabit & (256 << ear)) == 0:
			if ver:
				print(("Error @%04x: %04x %04x " +
				    "EA.7.%d illegal (%04x)") %
				    (adr, self.p.m.b16(adr), self.p.m.b16(adr + 2),
				    ear, eabit))
				print("\t", c)
			return (False, None, None)
		elif eam < 7 and (eabit & (1 << eam)) == 0:
			if ver:
				print(("Error @%04x: %04x %04x " +
				    "EA.%d illegal (%04x)") %
				    (adr, self.p.m.b16(adr), self.p.m.b16(adr + 2),
				    eam, eabit))
				print("\t", c)
			return (False, None, None)
		return (True, eam, ear)

	def findall(self, adr):
		lc = self.root.allfind(p, adr, p.m.b16)
		if len(lc) == 0:
			print("Error @%04x: %04x %04x no instruction found" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			return None
		elif len(lc) == 1:
			c = lc[0]
		else:
			i = 0
			print("@%04x:: %04x %04x" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			while i < len(lc):
				print("\t", lc[i])
				y = self.rdarg(adr, lc[i], "sz", True)
				if y == 3:
					#print("Elim sz\t", lc[i])
					del lc[i]
					continue
				if False:
					(junk, eam, ear) = \
					    self.check_valid_ea(ins, lc[i])
					if not junk:
						del lc[i]
						continue
				#print("\t", lc[i])
				i += 1

			if len(lc) == 1:
				c = lc[0]
			else:
				print(("Warning @%04x: %04x %04x " + 
				    "multiple ins found found") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
				for i in lc:
					print("\t", i)
				return None
		return c
		
	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"
		ins.gbd = False

		p = self.p
		try:
			c = self.root.find(p, adr, p.m.b16)
		except:
			ins.fail("no match", ask_gdb(p.m, adr) )
			return None

		# We have a specification in 'c'
		self.last_c = c
		ins.hi = adr + (c.width >> 3)

		mne = c.spec[0]

		if mne[-2:] == ".B":
			wid = 8
		elif mne[-2:] == ".W":
			wid = 16
		elif mne[-2:] == ".L":
			wid = 32
		elif mne[-2:] == ".Z":
			y = self.rdarg(adr, c, "sz")
			if y == 0:
				wid = 8
				mne = mne[:-1] + "B"
			elif y == 1:
				wid = 16
				mne = mne[:-1] + "W"
			elif y == 2:
				wid = 32
				mne = mne[:-1] + "L"
			else:
				#print(("Error @%04x: %04x %04x " +
				#    "Wrong 'sz' field") %
				#    (adr, p.m.b16(adr), p.m.b16(adr + 2)),
				#    y)
				#print("\t", c)
				#print(self.root.allfind(p, adr, p.m.b16))
				ins.fail("wrong sz field", 
					ask_gdb(p.m, adr)
				)
				return 
		
		else:
			wid = 16

		ol = list()
		cc = None
		ncc = None
		dstadr = None
		ea = None

		speclist = c.spec[1].split(",")

		if speclist[0] == "#data":
			if wid == 8:
				idata = "#0x%02x" % (p.m.b16(ins.hi) & 0xff)
				ins.hi += 2
			elif wid == 16:
				idata = "#0x%04x" % p.m.b16(ins.hi)
				ins.hi += 2
			elif wid == 32:
				idata = "#0x%08x" % p.m.b32(ins.hi)
				ins.hi += 4
			else:
				raise disass.DisassError("wrong wid #data")
		else:
			idata = None

		(junk, eam, ear) = self.check_valid_ea(ins, c)

		if junk == True:
			ea,dstadr = self.ea(ins, eam, ear, wid)
			if ea == None:
				ins.fail("wrong ea m<%x> r<%x>" % (eam, ear) +
					"\n\t" + ask_gdb(p.m, adr)
				)
				return
		else:
			ea = None
			dstadr = None

		for i in speclist:
			y = None
			if i == '""':
				y = None
			elif i == "ea":
				if ea == None:
					ins.fail("No ea",
					    "@" + p.m.afmt(adr) +
					    ": " + p.m.dfmt(p.m.b16(adr)) + 
					    " " + p.m.dfmt(p.m.b16(adr + 2)) +
					    " " + str(c) + "\n" +
					    "\t" + ask_gdb(p.m, adr)
					)
					return
				y = ea
			elif i == "An" or i == "Ax" or i == "Ay":
				y = "A%d" % self.rdarg(adr, c, i)
			elif i == "Dn" or i == "Dx" or i == "Dy":
				y = "D%d" % self.rdarg(adr, c, i)
			elif i == "-(Ax)" or i == "Ax" or i == "-(Ay)":
				y = "-(A%d)" % self.rdarg(adr, c, i[2:-1])
			elif i == "(Ax)+" or i == "Ax" or i == "(Ay)+":
				y = "(A%d)+" % self.rdarg(adr, c, i[1:-2])
			elif i == "#data":
				y = idata
			elif i == "#rot":
				j = self.rdarg(adr, c, i)
				if j == 0:
					j = 8
				y = "#%d" % j
			elif i == "#vect":
				y = "%d" % self.rdarg(adr, c, i) 
			elif i == "#const":
				y = "#0x%01x" % self.rdarg(adr, c, "const")
			elif i == "#word":
				y = "#0x%04x" % self.rdarg(adr, c, i)
			elif i == "An+#disp16":
				k = self.rdarg(adr, c, "An")
				j = self.rdarg(adr, c, "disp16")
				if j & 0x8000:
					y = "(A%d-0x%x)" % (k, -(j - 0x10000))
				else:
					y = "(A%d+0x%x)" % (k, j)
			elif i == "#disp16":
				j = self.rdarg(adr, c, i)
				if j & 0x8000:
					j -= 0x10000
				dstadr = adr + 2 + j
				#print("%04x: na=%04x j=%d" % (adr, ins.hi, j))
				y = "0x%04x" % dstadr
			elif i == "rrlist":
				y = regrlist(self.rdarg(adr, c, i))
			elif i == "rlist":
				y = reglist(self.rdarg(adr, c, i))
			elif i == "#bn":
				y = "#%d" % self.rdarg(adr, c, i)
			elif i == "#data8":
				y = "#0x%02x" % self.rdarg(adr, c, i)
			elif i == "#dst":
				# Used in Bcc
				j = self.rdarg(adr, c, "disp8")
				if j == 0x00:
					j = p.m.sb16(ins.hi)
					ins.hi += 2
				elif j == 0xff:
					j = p.m.sb32(ins.hi)
					ins.hi += 4
				elif j & 0x80:
					j -= 256
				dstadr = adr + 2 + j
				y = (dstadr, "%s")
			elif i == "ead":
				eadr = self.rdarg(adr, c, "earx")
				eadm = self.rdarg(adr, c, "eamx")
				(y, junk) = self.ea(ins, eadm, eadr, wid)
			elif i == "cc":
				cc = condition_codes[self.rdarg(adr, c, i)]
				if mne == "Bcc":
					mne = "B" + cc
				elif mne == "DBcc":
					mne = "DB" + cc
				else:
					y = cc
			elif i == "Rc":
				y = "RC%03x" % self.rdarg(adr, c, i)
			elif i in special_registers:
				y = i
			else:
				print(("Error @%04x: %04x %04x " +
				    "ARG '%s' not handled") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    i))
				print("\t", c)
				ins.fail("unhandled arg" + ask_gdb(p.m,adr))
				return
			if y != None:
				ol.append(y)

		if mne == "TRAP":
			ins.flow("call.TRAP", "T", None)
		elif mne[:2] == "DB":
			ins.flow("cond", "NZ", dstadr)
			ins.flow("cond", "Z", ins.hi)
		elif mne == "BRA":
			ins.flow("cond", "T", dstadr)
		elif mne == "JMP":
			ins.flow("cond", "T", dstadr)
		elif mne == "RTE":
			ins.flow("ret", "T", dstadr)
		elif mne == "RTS":
			ins.flow("ret", "T", dstadr)
		elif mne == "BSR":
			ins.flow("call", "T", dstadr)
		elif mne == "JSR":
			ins.flow("call", "T", dstadr)
		elif c.spec[0] == "DBcc" and cc != "F":
			ins.flow( "cond", cc, dstadr)
			ins.flow( "cond", cc, ins.hi)
		elif c.spec[0] == "Bcc":
			ins.flow("cond", cc, dstadr)
			ins.flow("cond", cc, ins.hi)
			
		ins.mne = mne
		if mne[0].islower() or ins.gbd:
			ins.lcmt(ask_gdb(p.m, adr) + "\tGDB\t" + str(self.last_c))
		ins.oper = ol

class m68000(m68k):
	def __init__(self, p, name = "m68000"):
		m68k.__init__(self, p, name)
		self.lew = False

class m68010(m68k):
	def __init__(self, p, name = "m68010"):
		m68k.__init__(self, p, name)
		self.load_ins("m68010_instructions.txt")
		self.lew = False

class m68020(m68k):
	def __init__(self, p, name = "m68020"):
		m68k.__init__(self, p, name)
		self.load_ins("m68010_instructions.txt")
		self.load_ins("m68020_instructions.txt")
		self.lew = True

class m68030(m68k):
	def __init__(self, p, name = "m68030"):
		m68k.__init__(self, p, name)
		self.load_ins("m68010_instructions.txt")
		self.load_ins("m68020_instructions.txt")
		self.load_ins("m68030_instructions.txt")
		self.lew = True

class m68040(m68k):
	def __init__(self, p, name = "m68040"):
		m68k.__init__(self, p, name)
		self.load_ins("m68010_instructions.txt")
		self.load_ins("m68020_instructions.txt")
		self.load_ins("m68030_instructions.txt")
		self.load_ins("m68040_instructions.txt")
		self.lew = True
