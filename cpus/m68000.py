#!/usr/local/bin/python
#
# Motorola M68000 CPU disassembler
#

from __future__ import print_function

import instree
import disass

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
	return "{" + r[1:] + "}"

#######################################################################

special_registers = {
	"USP", "CCR", "SR"
}

condition_codes = (
	"T",  "F",  "HI", "LS", "CC", "CS", "NE", "EQ",
	"VC", "VS", "PL", "MI", "GE", "LT", "GT", "LE"
)

class m68000(disass.assy):

	def __init__(self, p, name = "m68000"):
		disass.assy.__init__(self, p, name)
		self.root = instree.instree(
		    width = 16,
		    filename = __file__[:-3] + "_instructions.txt"
		)
		#self.root.print()

	def rdarg(self, adr, c, arg, fail_ok = False):
		x = c.get_field(self.p, adr, self.p.m.b16, 2, arg)
		if x == None and not fail_ok:
			print("NB: ", arg, "not found in", c)
		return x

	def extword(self, ins, idx):
		adr = ins.lo
		p = self.p
		ev = p.m.b16(ins.hi)
		ins.hi += 2
		if ev & 256:
			print(("Error @%04x: %04x %04x " +
			    "Long extension word in EA.6 %04x") %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2),
			    ev))
			print("\t", self.last_c)
			return None
		#print("EA6: Ev: %04x" % ev)
		da = ev >> 15
		reg = (ev >> 12) & 7
		wl = (ev >> 11) & 1
		scale = (ev >> 9) & 3
		displ = ev & 0xff
		if displ & 0x80:
			displ -= 256
		if da == 0:
			rg = "D%d" % reg
		else:
			rg = "A%d" % reg
		if wl:
			rg += ".L"
		else:
			rg += ".W"
		#print("rg", rg, "wl", wl, "scale", scale, "displ", displ)
		ea="(%s" % rg
		if displ < 0:
			ea +=  "-0x%x+" % -displ
		elif displ > 0:
			ea +=  "+0x%x+" % displ
		if scale != 0:
			ea +=  "%d*" % (1 << scale)
		ea += idx + ")"
		return ea

	def ea(self, ins, eam, ear, wid):

		adr = ins.lo
		v = None
		if eam == 0:
			ea = "D%d" % ear
		elif eam == 1:
			ea = "A%d" % ear
		elif eam == 2:
			ea = "(A%d)" % ear
		elif eam == 3:
			ea = "(A%d)+" % ear
		elif eam == 4:
			ea = "-(A%d)" % ear
		elif eam == 5:
			v = self.p.m.sb16(ins.hi)
			ins.hi += 2
			if v < 0:
				ea = "(A%d-#0x%04x)" % (ear, -v)
			else:
				ea = "(A%d+#0x%04x)" % (ear, v)
		elif eam == 6:
			ea = self.extword(ins, "A%d" % ear)
			if ea == None:
				return (None, None)
		elif eam == 7 and ear == 0:
			v = self.p.m.b16(ins.hi)
			# XXX: signextend
			ea="#0x%04x" % v
			ins.hi += 2
		elif eam == 7 and ear == 1:
			v =self.p.m.b32(ins.hi)
			ea="#0x%08x" % v
			ins.hi += 4
		elif eam == 7 and ear == 2:
			v = ins.hi + self.p.m.sb16(ins.hi)
			ea="#0x%08x" % v
			ins.hi += 2
		elif eam == 7 and ear == 3:
			ea = self.extword(ins, "PC")
			if ea == None:
				return (None, None)
		elif eam == 7 and ear == 4 and wid == 8:
			ea="#0x%04x" % (self.p.m.b16(ins.hi) & 0xff)
			ins.hi += 2
		elif eam == 7 and ear == 4 and wid == 16:
			v = self.p.m.b16(ins.hi)
			ea="#0x%04x" % v
			ins.hi += 2
		elif eam == 7 and ear == 4 and wid == 32:
			v = self.p.m.b32(ins.hi)
			ea="#0x%08x" % v
			ins.hi += 4
		else:
			print(("Error @%04x: %04x %04x " +
			    "EA.%d.%d w%d missing") %
			    (adr, self.p.m.b16(adr), self.p.m.b16(adr + 2),
			    eam, ear, wid))
			print("\t", self.last_c)
			return (None, None)
		#print("\team=", eam, "ear=", ear, "wid=%d" % wid, "ins.hi=%x" % ins.hi,"->", ea, v)
		return (ea, v)
		
	def check_valid_ea(self, ins, c, ver = True):
		# Figure out Effective Address
		eabit = int(c.spec[2],16)
		if eabit == 0:
			return (None, 0, 0)

		adr = ins.lo

		if eabit & 0xe080:
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

		p = self.p
		#print(">>> @%04x" % adr)
		try:
			c = self.root.find(p, adr, p.m.b16)
		except:
			ins.fail("no memory")
			return
		if c == None:
			print("Error @%04x: %04x %04x no instruction found" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			ins.fail("no instruction")
			return
		#print("]]} @%04x" % adr, c)

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
				print(("Error @%04x: %04x %04x " +
				    "Wrong 'sz' field") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2)),
				    y)
				print("\t", c)
				print(self.root.allfind(p, adr, p.m.b16))
				ins.fail("wrong sz field")
				return 
		
		else:
			wid = 16

		ol = list()
		cc = None
		ncc = None
		dstadr = None
		ea = None

		(junk, eam, ear) = self.check_valid_ea(ins, c)

		if junk == True:
			ea,dstadr = self.ea(ins, eam, ear, wid)
			if ea == None:
				ins.fail("wrong ea")
				return

		for i in c.spec[1].split(","):
			y = None
			if i == '""':
				y = None
			elif i == "ea":
				if ea == None:
					print(("Error @%04x: %04x %04x " +
					    "expected EA") %
					    (adr, p.m.b16(adr), p.m.b16(adr + 2)
					    ))
					print("\t", c)
					ins.fail("wrong ea")
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
			elif i == "#data" and wid == 8:
				y = "#0x%02x" % (p.m.b16(ins.hi) & 0xff)
				ins.hi += 2
			elif i == "#data" and wid == 16:
				y = "#0x%04x" % p.m.b16(ins.hi)
				ins.hi += 2
			elif i == "#data" and wid == 32:
				y = "#0x%08x" % p.m.b32(ins.hi)
				ins.hi += 4
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
				#print("DA %04x:%04x %x %04x" % 
				#   (adr, ins.hi, j, dstadr))
				y = "0x%x" % dstadr
			elif i == "ead":
				eadr = self.rdarg(adr, c, "earx")
				eadm = self.rdarg(adr, c, "eamx")
				(y, junk) = \
				    self.ea(ins, eadm, eadr, wid)
			elif i == "cc":
				cc = condition_codes[self.rdarg(adr, c, i)]
				if mne == "Bcc":
					mne = "B" + cc
				elif mne == "DBcc":
					mne = "DB" + cc
				else:
					y = cc
			elif i in special_registers:
				y = i
			else:
				print(("Error @%04x: %04x %04x " +
				    "ARG '%s' not handled") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    i))
				print("\t", c)
				ins.fail("unhandled arg")
				return
			if y != None:
				ol.append(y)

		if mne == "TRAP":
			ins.flow("call.TRAP", "T", None)
		if mne == "BRA":
			ins.flow("cond", "T", dstadr)
		elif mne == "JMP":
			ins.flow("cond", "T", dstadr)
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
		ins.oper = ol
