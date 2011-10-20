#!/usr/local/bin/python
#
# Zilog Z800[12] CPU disassembler
#

import instree
import disass

#######################################################################

special_registers = {
	"FLAGS":	True,
	"FCW":		True,
	"PSAOFF":	True,
	"PSAPSEG":	True,
	"NSPSEG":	True,
	"NSPOFF":	True,
	"REFRESH":	True,
}

condition_codes = {
	0:	"F", 	8:	"T",
	1:	"LT",	9:	"GE",
	2:	"LE",	10:	"GT",
	3:	"ULE",	11:	"UGT",
	4:	"PE",	12:	"PO",
	5:	"MI",	13:	"PL",
	6:	"Z",	14:	"NZ",
	7:	"C",	15:	"NC"
}

class z8000(disass.assy):

	def __init__(self, p, name = "z8000", z8001 = True, segmented = False):
		disass.assy.__init__(self, p, name)
		if segmented:
			assert z8001
		self.z8001 = z8001
		self.segmented = segmented
		self.root = instree.instree(
		    width = 16,
		    filename = __file__[:-3] + "_instructions.txt"
		)
		#self.root.print()

	def rdarg(self, p, adr, c, arg):
		return c.get_field(p, adr, p.m.b16, 2, arg)

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

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		p = self.p

		# By default...
		ins.hi = ins.lo + 1

		#print(">>> @%04x" % adr)
		try:
			c = self.root.find(p, adr, p.m.b16)
		except:
			ins.fail("no memory")
			return
		if c == None:
			ins.fail("no instruction")
			return
			print("Error @%04x: %04x %04x no instruction found" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			return None

		#print("]]} @%04x" % adr, c)

		# We have a specification in 'c'
		self.last_c = c
		na = adr + (c.width >> 3)

		mne = c.spec[0]

		# Try to divine the width of this instruction
		wid = 16
		if mne[-3:] == "CTL":
			pass
		elif mne == "SLL":
			pass
		elif mne == "SUB":
			pass
		elif mne[-1] == "L":
			wid = 32
		elif mne[-1] == "B":
			wid = 8

		i = self.rdarg(p, adr, c, "W")
		if i != None:
			w = i
			if w == 0:
				wid = 8
				mne += "B"
			elif w == 1:
				wid = 16

		# Try to divine the src/dest-addr sizes
		if self.segmented:
			das = 32
			sas = 32
		else:
			das = 16
			sas = 16

		if mne[:4] == "OTIR":
			das = 16
			i = self.rdarg(p, adr, c, "S")
			assert i != None
			if i == 1:
				mne = "S" + mne

		#print(">>> %04x" % adr, wid, sas, das, c)

		ol = list()
		cc = None
		ncc = None
		dstadr = None
		for i in c.spec[1].split(","):
			y = i
			if i in special_registers:
				pass
			elif i == '""':
				continue
			elif i == "Rd":
				i = self.get_reg(p, adr, "Rd", c, wid)
			elif i == "RRd":
				i = self.get_reg(p, adr, "RRd", c, 32)
			elif i == "RRs":
				i = self.get_reg(p, adr, "RRs", c, 32)
			elif i == "Rbd":
				i = self.get_reg(p, adr, "Rbd", c, 8)
			elif i == "Rbs":
				i = self.get_reg(p, adr, "Rbs", c, 8)
			elif i == "Rbl":
				i = self.get_reg(p, adr, "Rbl", c, 8)
			elif i == "Rs":
				i = self.get_reg(p, adr, "Rs", c, wid)
			elif i == "Rbd":
				assert wid == 8
				i = self.get_reg(p, adr, "Rbd", c, 8)
			elif i == "int":
				j = self.rdarg(p, adr, c, "int")
				i = "<int:%x>" % j
			elif i == "port":
				j = self.rdarg(p, adr, c, "port")
				i = "0x%04x" % j
			elif i == "#nibble":
				j = self.rdarg(p, adr, c, "nibble")
				i = "0x%01x" % j
			elif i == "flags":
				j = self.rdarg(p, adr, c, "flags")
				i = "<flags=%x>" % j
			elif i == "#src":
				j = self.rdarg(p, adr, c, "src")
				i = "#0x%02x" % j
			elif i == "#byte":
				j = self.rdarg(p, adr, c, "byte")
				i = "0x%02x" % j
			elif i == "dispu8":
				# D[B]JNZ
				j = self.rdarg(p, adr, c, "dispu8")
				dstadr = na - 2 * j
				i = "0x%04x" % dstadr
			elif i == "disp8":
				j = self.rdarg(p, adr, c, "disp8")
				if j > 127:
					j -= 256
				dstadr = na + 2 * j
				i = "0x%04x" % dstadr
			elif i == "disp12":
				j = self.rdarg(p, adr, c, "disp12")
				if j > 2047:
					j -= 4096
				dstadr = na - 2 * j
				i = "0x%04x" % dstadr
			elif i == "#S":
				j = self.rdarg(p, adr, c, "S")
				i = "#%d" % (j + 1)
			elif i == "#n":
				j = self.rdarg(p, adr, c, "n-1")
				i = "#%d" % (j + 1)
			elif i == "#b":
				j = self.rdarg(p, adr, c, "b")
				if mne[:2] == "SL" and j > 127:
					mne = "SR" + mne[3:]
					j = 256 - j
				i = "%d" % j
			elif i == "#data" and wid == 8:
				d = p.m.b16(na)
				if (d >> 8) != (d & 0xff):
					print(
					    "Warning: @%04x %04x %04x: " %
					    (adr, p.m.b16(adr),
					    p.m.b16(adr + 2)) +
					    "8-bit #data not duplicated" +
					    " 0x%04x" % d)
					ins.fail("#data(8) not duplicated")
					return
				na += 2
				i = "#0x%02x" % (d & 0xff)
			elif i == "#data" and wid == 16:
				d = p.m.b16(na)
				na += 2
				i = "#0x%04x" % d
			elif i == "address":
				(na, d1, d2, i) = self.get_address(p, na)
				dstadr = d1
			elif i == "addr(Rs)":
				j = self.get_reg(p, adr, "Rs", c, 16)
				(na, d1, d2, i) = self.get_address(p, na)
				i += "(%s)" % j
			elif i == "addr(Rd)":
				j = self.get_reg(p, adr, "Rd", c, 16)
				(na, d1, d2, i) = self.get_address(p, na)
				i += "(%s)" % j
			elif i == "@Rs":
				i = "@" + self.get_reg(p, adr, "Rs", c, sas)
			elif i == "@Rd":
				i = "@" + self.get_reg(p, adr, "Rd", c, das)
			elif i == "Rs(#disp16)":
				rs = self.get_reg(p, adr, "Rs", c, das)
				d16 = self.rdarg(p, adr, c, "disp16")
				i = "%s(#0x%04x)" % (rs, d16)
			elif i == "Rd(#disp16)":
				rd = self.get_reg(p, adr, "Rd", c, das)
				d16 = self.rdarg(p, adr, c, "disp16")
				i = "%s(#0x%04x)" % (rd, d16)
			elif i == "Rd(Rx)":
				rd = self.get_reg(p, adr, "Rd", c, das)
				rx = self.get_reg(p, adr, "Rx", c, das)
				i = "%s(%s)" % (rd, rx)
			elif i == "Rs(Rx)":
				rs = self.get_reg(p, adr, "Rs", c, das)
				rx = self.get_reg(p, adr, "Rx", c, das)
				i = "%s(%s)" % (rs, rx)
			elif i == "r":
				i = self.get_reg(p, adr, "r", c, 16)
			elif i == "cc":
				v = self.rdarg(p, adr, c, "cc")
				cc = condition_codes[v]
				ncc = condition_codes[v ^ 8]
				i = cc
			else:
				print(">>> %04x" % adr, wid, sas, das, c)
				print(y, "???", i)
				ins.fail('Unhandled arg')
				return
			if y != i and False:
				print(y, "-->", i)
			ol.append(i)
			
		if mne[0] == "J":
			if cc != "F":
				ins.flow( "cond", cc, dstadr)
			if ncc != "F":
				ins.flow( "cond", ncc, na)

		if mne == "CALR":
			ins.flow( "call", "T", dstadr)
		if mne == "CALL":
			ins.flow( "call", "T", dstadr)
		if mne == "RET" and cc == "T":
			ins.flow( "ret", "T", None)

		#if dstadr != None:
		#	x.a['DA'] = dstadr

		ins.hi = na
		ins.mne = mne
		ins.oper = ol
