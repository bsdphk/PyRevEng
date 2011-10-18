#!/usr/local/bin/python
#
# Motorola M68000 CPU disassembler
#

from __future__ import print_function

import instree
import sys

#######################################################################

special_registers = {
}

condition_codes = (
	"T",  "F",  "HI", "LS", "CC", "CS", "NE", "EQ",
	"VC", "VS", "PL", "MI", "GE", "LT", "GT", "LE"
)

class m68000(object):

	def __init__(self, z8001 = True, segmented = False):
		self.dummy = True
		if segmented:
			assert z8001
		self.z8001 = z8001
		self.segmented = segmented
		self.root = instree.instree(
		    width = 16,
		    filename = "m68000_instructions.txt",
		)
		#self.root.print()

	def render(self, p, t):
		s = t.a['mne']
		s += "\t"
		d = ""
		if 'DA' in t.a:
			da = t.a['DA']
			if da in p.label:
				return (s + p.label[da] +
				    " (" + p.m.afmt(da) + ")",)
		for i in t.a['oper']:
			s += d
			s += str(i)
			d = ','
		return (s,)

	def rdarg(self, p, adr, c, arg, fail_ok = False):
		x = c.get_field(p, adr, p.m.b16, 2, arg)
		if x == None and not fail_ok:
			print("NB: ", arg, "not found in", c)
		return x

	def get_reg(self, p, adr, arg, c, wid):
		if arg in c.flds:
			v = self.rdarg(p, adr, c, arg)
		elif arg + "!=0" in c.flds:
			v = self.rdarg(p, adr, c, arg + "!=0")
			if v == 0:
				print("Error @%04x: %04x %04x  %s == 0" %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    arg + "!=0"), c.flds[arg + "!=0"])
				return None
		else:
			print("Error @%04x: %04x %04x  not found %s" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2), arg))
			assert False
		if wid == 32:
			if (v & 1) == 1:
				print("Error @%04x: %04x %04x  RR%d" %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2), v))
				assert False
			return "RR%d" % v
		if wid == 16:
			return "R%d" % v
		if wid == 8 and v & 8:
			return "RL%d" % (v & 7)
		if wid == 8:
			return "RH%d" % (v & 7)

	def get_address(self, p, na):
		d1 = p.m.b16(na)
		na += 2
		i = "#0x%04x" % d1
		if self.segmented and d1 & 0x8000:
			d2 = p.m.b16(na)
			na += 2
			i += ":0x%04x" % d2
		else:
			d2 = None
		return (na, d1, d2, i)

	def disass(self, p, adr, priv = None):
		sys.stdout.flush()
		self.last_c = None
		if True:
			x = self.xdisass(p, adr, priv)
			return x

		try:
			x = self.xdisass(p, adr, priv)
		except:
			try:
				print("Error @%04x: %04x %04x disass failed" %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			except:
				print("Error @%04x" % adr)
			if self.last_c != None:
				print("\t", self.last_c)
			x = None
		return x

	def extword(self, p, adr, na, idx):
		ev = p.m.b16(na)
		na += 2
		if ev & 256:
			print(("Error @%04x: %04x %04x " +
			    "Long extension word in EA.6 %04x") %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2),
			    ev))
			print("\t", self.last_c)
			return (None, na)
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
		return (ea,na)

	def ea(self, p, adr, na, eam, ear, wid):
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
			v = p.m.sb16(na)
			na += 2
			if v < 0:
				ea = "(A%d-#0x%04x)" % (ear, -v)
			else:
				ea = "(A%d+#0x%04x)" % (ear, v)
		elif eam == 6:
			ea,na = self.extword(p, adr, na, "A%d" % ear)
			if ea == None:
				return (na, None, None)
		elif eam == 7 and ear == 0:
			v = p.m.b16(na)
			# XXX: signextend
			ea="#0x%04x" % v
			na += 2
		elif eam == 7 and ear == 1:
			v =p.m.b32(na)
			ea="#0x%08x" % v
			na += 4
		elif eam == 7 and ear == 2:
			v = na + p.m.sb16(na)
			ea="#0x%08x" % v
			na += 2
		elif eam == 7 and ear == 3:
			ea,na = self.extword(p, adr, na, "PC")
			if ea == None:
				return (na, None, None)
		elif eam == 7 and ear == 4 and wid == 8:
			ea="#0x%04x" % (p.m.b16(na) & 0xff)
			na += 2
		elif eam == 7 and ear == 4 and wid == 16:
			v = p.m.b16(na)
			ea="#0x%04x" % v
			na += 2
		elif eam == 7 and ear == 4 and wid == 32:
			v = p.m.b32(na)
			ea="#0x%08x" % v
			na += 4
		else:
			print(("Error @%04x: %04x %04x " +
			    "EA.%d.%d w%d missing") %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2),
			    eam, ear, wid))
			print("\t", self.last_c)
			return (na, None, None)
		#print("\team=", eam, "ear=", ear, "wid=%d" % wid, "na=%x" % na,"->", ea, v)
		return (na, ea, v)
		
	def check_valid_ea(self, p, adr, c, ver = True):
		# Figure out Effective Address
		eabit = int(c.spec[2],16)
		if eabit == 0:
			return (None, 0, 0)

		if eabit & 0xe080:
			print("Error @%04x: %04x %04x " +
			    "EAbits illegal (%04x)" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2),
			    eabit))
			print("\t", c)
			return (False, None, None)

		eam = self.rdarg(p, adr, c, "eam")
		ear = self.rdarg(p, adr, c, "ear")

		if eam == 7 and (eabit & (256 << ear)) == 0:
			if ver:
				print(("Error @%04x: %04x %04x " +
				    "EA.7.%d illegal (%04x)") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    ear, eabit))
				print("\t", c)
			return (False, None, None)
		elif eam < 7 and (eabit & (1 << eam)) == 0:
			if ver:
				print(("Error @%04x: %04x %04x " +
				    "EA.%d illegal (%04x)") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
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
				y = self.rdarg(p, adr, lc[i], "sz", True)
				if y == 3:
					#print("Elim sz\t", lc[i])
					del lc[i]
					continue
				if False:
					(junk, eam, ear) = \
					    self.check_valid_ea(p, adr, lc[i])
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
		
	def xdisass(self, p, adr, priv = None):
		if p.t.find(adr, "ins") != None:
			return

		#print(">>> @%04x" % adr)
		c = self.root.find(p, adr, p.m.b16)
		#print("]]} @%04x" % adr, c)

		# We have a specification in 'c'
		self.last_c = c
		na = adr + (c.width >> 3)

		mne = c.spec[0]

		if mne[-2:] == ".B":
			wid = 8
		elif mne[-2:] == ".W":
			wid = 16
		elif mne[-2:] == ".L":
			wid = 32
		elif mne[-2:] == ".Z":
			y = self.rdarg(p, adr, c, "sz")
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
				return None
		
		else:
			wid = 16

		ol = list()
		cc = None
		ncc = None
		dstadr = None
		ea = None

		(junk, eam, ear) = self.check_valid_ea(p, adr, c)

		if junk == True:
			na,ea,dstadr = self.ea(p, adr, na, eam, ear, wid)
			if ea == None:
				return None

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
					return None
				y = ea
			elif i == "An" or i == "Ax" or i == "Ay":
				y = "A%d" % self.rdarg(p, adr, c, i)
			elif i == "Dn" or i == "Dx" or i == "Dy":
				y = "D%d" % self.rdarg(p, adr, c, i)
			elif i == "#data" and wid == 8:
				y = "#0x%02x" % (p.m.b16(na) & 0xff)
				na += 2
			elif i == "#data" and wid == 16:
				y = "#0x%04x" % p.m.b16(na)
				na += 2
			elif i == "#data" and wid == 32:
				y = "#0x%08x" % p.m.b32(na)
				na += 4
			elif i == "#rot":
				j = self.rdarg(p, adr, c, i)
				if j == 0:
					j = 8
				y = "#%d" % j
			elif i == "#vect":
				y = "%d" % self.rdarg(p, adr, c, i) 
			elif i == "#const":
				y = "#0x%01x" % self.rdarg(p, adr, c, "const")
			elif i == "#word":
				y = "#0x%04x" % self.rdarg(p, adr, c, i)
			elif i == "An+#disp16":
				k = self.rdarg(p, adr, c, "An")
				j = self.rdarg(p, adr, c, "disp16")
				if j & 0x8000:
					y = "(A%d-0x%x)" % (k, -(j - 0x10000))
				else:
					y = "(A%d+0x%x)" % (k, j)
			elif i == "#disp16":
				j = self.rdarg(p, adr, c, i)
				if j & 0x8000:
					j -= 0x10000
				dstadr = adr + 2 + j
				#print("%04x: na=%04x j=%d" % (adr, na, j))
				y = "0x%04x" % dstadr
			elif i == "rlist":
				y = "<%x>" % self.rdarg(p, adr, c, i)
			elif i == "#bn":
				y = "#%d" % self.rdarg(p, adr, c, i)
			elif i == "#data8":
				y = "#0x%02x" % self.rdarg(p, adr, c, i)
			elif i == "#dst":
				# Used in Bcc
				j = self.rdarg(p, adr, c, "disp8")
				if j == 0x00:
					j = p.m.sb16(na)
					na += 2
				elif j == 0xff:
					j = p.m.sb32(na)
					na += 4
				elif j & 0x80:
					j -= 256
				dstadr = adr + 2 + j
				#print("DA %04x:%04x %x %04x" % 
				#   (adr, na, j, dstadr))
				y = "0x%x" % dstadr
			elif i == "ead":
				eadr = self.rdarg(p, adr, c, "earx")
				eadm = self.rdarg(p, adr, c, "eamx")
				(na, y, junk) = \
				    self.ea(p, adr, na, eadm, eadr, wid)
			elif i == "cc":
				cc = condition_codes[self.rdarg(p, adr, c, i)]
				if mne == "Bcc":
					mne = "B" + cc
				elif mne == "DBcc":
					mne = "DB" + cc
				else:
					y = cc
			elif i == "CCR":
				y = i
			elif i == "USP":
				y = i
			elif i == "SR":
				y = i
			else:
				print(("Error @%04x: %04x %04x " +
				    "ARG '%s' not handled") %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    i))
				print("\t", c)
				return None
			if y != None:
				ol.append(y)
			
		try:
			x = p.t.add(adr, na, "ins")
		except:
			print("Error: @%04x %04x %04x: overlap" %
			    (adr, p.m.b16(adr),
			    p.m.b16(adr + 2)))
			print("\t", c)
			return None
			
		x.a['mne'] = mne
		x.a['oper'] = ol
		x.render = self.render

		if mne == "TRAP":
			x.a['flow'] = ()
		if mne == "BRA":
			x.a['flow'] = ( ( "cond", "T", dstadr), )
		elif mne == "JMP":
			x.a['flow'] = ( ( "cond", "T", dstadr), )
		elif mne == "RTS":
			x.a['flow'] = ( ( "ret", "T", dstadr), )
		elif mne == "BSR":
			x.a['flow'] = ( ( "call", "T", dstadr), )
		elif mne == "JSR":
			x.a['flow'] = ( ( "call", "T", dstadr), )
		elif c.spec[0] == "DBcc" and cc != "F":
			x.a['flow'] = (
				( "cond", cc, dstadr), 
				( "cond", cc, na), 
			)
		elif c.spec[0] == "Bcc":
			x.a['flow'] = (
				( "cond", cc, dstadr), 
				( "cond", cc, na), 
			)

		p.ins(x, self.disass)
		# print(">>> @%04x" % adr)
