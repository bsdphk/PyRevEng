#!/usr/local/bin/python
#
# Zilog Z800[12] CPU disassembler
#

from __future__ import print_function

#######################################################################
# Parse a "([01x] )*[01x]" string into a mask + bits

def parse_match(bit, f):
	mask = 0
	bits = 0
	width = 0
	l = len(f)
	if l & 1 == 0:
		return None
	i = 0
	while i < l:
		mask <<= 1
		bits <<= 1
		width += 1
		if f[i] == "0":
			mask |= 1
		elif f[i] == "1":
			mask |= 1
			bits |= 1
		elif f[i] == "x":
			pass
		else:
			return None
		i += 1
		if i < l and f[i] != " ":
			return None
		i += 1
	return (bit, width, mask, bits)

#######################################################################
# Collapse a list of (start, width, mask, bits) into a list of
# unit width (mask, bits)'s.

def collapse(l, unit):
	i = 0
	ln = list()
	mask = 0
	bits = 0
	b = 0
	for i in l:
		while i[0] >= b+unit:
			#ln.append("%04x %04x" % (mask, bits))
			ln.append((mask, bits))
			mask = 0
			bits = 0
			b += unit
		s = (2 * unit - (i[0]+i[1])) % unit
		if s == unit:
			s = 0
		mask |= i[2] << s
		bits |= i[3] << s
	if mask != 0:
		ln.append((mask, bits))
	return ln

#######################################################################
# Add instruction to tree
#
# XXX: handle multiple words

def add_ins(ilist, la, bit, mne, oper, lb):
	x = (la, bit, mne, oper, lb)
	for i in ilist:
		if la[0][0] != i[0]:
			continue
		y = la[0][1]
		if y in i[1]:
			print("Coll")
			print("\t", "%04x %04x" % la[0], x)
			z = i[1][y]
			print("\t", "%04x %04x" % z[0][0], z)
			return
		i[1][la[0][1]] = x
		return

	d = dict()
	d[la[0][1]] = x
	e = (la[0][0], d)

	# Insert new entry into ilist ahead of any masks which are
	# a subset of the current mask.
	#
	# XXX: Where masks conflict, (ie: 0xff0f and 0xfff0) we expect
	# the instruction set to be defined sensibly.
	#
	for i in range(0, len(ilist)):
		x = ilist[i]
		c = ~(x[0] & e[0])
		if c & x[0] == 0:
			ilist.insert(i, e)
			return
	# Otherwise append
	ilist.append(e)

#######################################################################

def parse_ins(unit=16):
	ilist = list()
	errors = 0
	f = open("z8000_instructions.txt", "r")
	z8_instructions = f.read()
	f.close()

	for i in z8_instructions.split("\n"):
		j=i.expandtabs().strip()
		if j == "" or j[0] == "#":
			continue
		k = j.split("|")
		l = k[0].split()
		mne = l[0]
		oper = l[1].split(",")
		del k[0]
		#print(mne,oper)
		la = list()
		lb = dict()
		bit = 0
		for j in  k:
			m = parse_match(bit, j)
			if m == None:
				k = j.strip()
				if k.find(" ") != -1:
					print("Error: space in field '%s'\n\t%s" % (j, i))
					errors += 1
				w = int((len(j) + 1)/2)
				m = (bit, w, j.strip())
				lb[j.strip()] = m
			else:
				la.append(m)
			bit += m[1]
		if bit % unit != 0:
			print("Error: Wrong number of bits: %d\n\t%s" % (bit, i))
		#print(">", mne, oper, la, lb)
		la = collapse(la, unit)
		add_ins(ilist, la, bit, mne, oper, lb)
	if errors > 0:
		exit(2)
	return ilist

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

class z8000(object):
	def __init__(self, z8001 = True, segmented = False):
		self.dummy = True
		if segmented:
			assert z8001
		self.z8001 = z8001
		self.segmented = segmented
		self.ilist = parse_ins()

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

	def rdarg(self, p, adr, arg):
		# arg = (12, 4, "Rd")
		o = arg[0]
		while o >= 16:
			adr += 2
			o -= 16;
		i = p.m.b16(adr)
		if o + arg[1] < 16:
			i >>= (16 - (o + arg[1]))
		i &= (1 << arg[1]) - 1
		#print("RA", "%04x" % adr, arg, "-> %04x" % i)
		return i

	def get_reg(self, p, adr, arg, c, wid):
		if arg in c:
			v = self.rdarg(p, adr, c[arg])
		elif arg + "!=0" in c:
			v = self.rdarg(p, adr, c[arg + "!=0"])
			if v == 0:
				print("Error @%04x: %04x %04x  %s == 0" %
				    (adr, p.m.b16(adr), p.m.b16(adr + 2),
				    arg + "!=0"))
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
		self.last_c = None
		if False:
			x = self.xdisass(p, adr, priv)
		try:
			x = self.xdisass(p, adr, priv)
		except:
			print("Error @%04x: %04x %04x disass failed" %
			    (adr, p.m.b16(adr), p.m.b16(adr + 2)))
			if self.last_c != None:
				print("\t", self.last_c)
			x = None
		return x
		
	def xdisass(self, p, adr, priv = None):
		if p.t.find(adr, "ins") != None:
			return
		try:
			iw = p.m.b16(adr)
			iw2 = p.m.b16(adr + 2)
		except:
			print("FETCH failed:", p.m.afmt(adr))
			return

		c = None
		for i in self.ilist:
			ii = iw & i[0]
			if not ii in i[1]:
				continue
			#print("Fnd:", i[1][ii])
			c = i[1][ii]
			break
		if c == None:
			print("None Found %04x %04x %04x" % (adr, iw, iw2))
			return

		# We have a specification in 'c'
		self.last_c = c
		na = adr + (c[1] >> 3)

		mne = c[2]

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

		if 'W' in c[4]:
			w = self.rdarg(p, adr, c[4]["W"])
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
			if self.rdarg(p, adr, c[4]["S"]):
				mne = "S" + mne

		#print(">>> %04x" % adr, wid, sas, das, c)

		ol = list()
		cc = None
		ncc = None
		dstadr = None
		for i in c[3]:
			y = i
			if i in special_registers:
				pass
			elif i == '""':
				continue
			elif i == "Rd":
				i = self.get_reg(p, adr, "Rd", c[4], wid)
			elif i == "RRd":
				i = self.get_reg(p, adr, "RRd", c[4], 32)
			elif i == "RRs":
				i = self.get_reg(p, adr, "RRs", c[4], 32)
			elif i == "Rbd":
				i = self.get_reg(p, adr, "Rbd", c[4], 8)
			elif i == "Rbs":
				i = self.get_reg(p, adr, "Rbs", c[4], 8)
			elif i == "Rbl":
				i = self.get_reg(p, adr, "Rbl", c[4], 8)
			elif i == "Rs":
				i = self.get_reg(p, adr, "Rs", c[4], wid)
			elif i == "Rbd":
				assert wid == 8
				i = self.get_reg(p, adr, "Rbd", c[4], 8)
			elif i == "int":
				j = self.rdarg(p, adr, c[4]["int"])
				i = "<int:%x>" % j
			elif i == "port":
				j = self.rdarg(p, adr, c[4]["port"])
				i = "0x%04x" % j
			elif i == "#nibble":
				j = self.rdarg(p, adr, c[4]["nibble"])
				i = "0x%01x" % j
			elif i == "flags":
				j = self.rdarg(p, adr, c[4]["flags"])
				i = "<flags=%x>" % j
			elif i == "#src":
				j = self.rdarg(p, adr, c[4]["src"])
				i = "#0x%02x" % j
			elif i == "#byte":
				j = self.rdarg(p, adr, c[4]["byte"])
				i = "0x%02x" % j
			elif i == "dispu8":
				j = self.rdarg(p, adr, c[4]["dispu8"])
				dstadr = na - 2 * j
				i = "0x%04x" % dstadr
			elif i == "disp8":
				j = self.rdarg(p, adr, c[4]["disp8"])
				if j > 127:
					j -= 256
				dstadr = na + 2 * j
				i = "0x%04x" % dstadr
			elif i == "disp12":
				j = self.rdarg(p, adr, c[4]["disp12"])
				if j > 2047:
					j -= 4096
				dstadr = na - 2 * j
				i = "0x%04x" % dstadr
			elif i == "#S":
				j = self.rdarg(p, adr, c[4]["S"])
				i = "#%d" % (j + 1)
			elif i == "#n":
				j = self.rdarg(p, adr, c[4]["n-1"])
				i = "#%d" % (j + 1)
			elif i == "#b":
				j = self.rdarg(p, adr, c[4]["b"])
				if mne[:2] == "SL" and j > 127:
					mne = "SR" + mne[3:]
					j = 256 - j
				i = "%d" % j
			elif i == "#data" and wid == 8:
				d = p.m.b16(na)
				if (d >> 8) != (d & 0xff):
					print("Warning: 8-bit #data not duplicated 0x%04x" % d)
					assert False
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
				j = self.get_reg(p, adr, "Rs", c[4], 16)
				(na, d1, d2, i) = self.get_address(p, na)
				i += "(%s)" % j
			elif i == "addr(Rd)":
				j = self.get_reg(p, adr, "Rd", c[4], 16)
				(na, d1, d2, i) = self.get_address(p, na)
				i += "(%s)" % j
			elif i == "@Rs":
				i = "@" + self.get_reg(p, adr, "Rs", c[4], sas)
			elif i == "@Rd":
				i = "@" + self.get_reg(p, adr, "Rd", c[4], das)
			elif i == "Rs(#disp16)":
				rs = self.get_reg(p, adr, "Rs", c[4], das)
				d16 = self.rdarg(p, adr, c[4]["disp16"])
				i = "%s(#0x%04x)" % (rs, d16)
			elif i == "Rd(#disp16)":
				rd = self.get_reg(p, adr, "Rd", c[4], das)
				d16 = self.rdarg(p, adr, c[4]["disp16"])
				i = "%s(#0x%04x)" % (rd, d16)
			elif i == "Rd(Rx)":
				rd = self.get_reg(p, adr, "Rd", c[4], das)
				rx = self.get_reg(p, adr, "Rx", c[4], das)
				i = "%s(%s)" % (rd, rx)
			elif i == "Rs(Rx)":
				rs = self.get_reg(p, adr, "Rs", c[4], das)
				rx = self.get_reg(p, adr, "Rx", c[4], das)
				i = "%s(%s)" % (rs, rx)
			elif i == "r":
				i = self.get_reg(p, adr, "r", c[4], 16)
			elif i == "cc":
				v = self.rdarg(p, adr, c[4]["cc"])
				cc = condition_codes[v]
				ncc = condition_codes[v ^ 8]
				i = cc
			else:
				print(">>> %04x" % adr, wid, sas, das, c)
				print(y, "???", i)
				return
			if y != i and False:
				print(y, "-->", i)
			ol.append(i)
			
		x = p.t.add(adr, na, "ins")
		x.a['mne'] = mne
		x.a['oper'] = ol
		x.render = self.render

		if mne[0] == "J":
			if cc != "F":
				x.a['flow'] = ( ( "cond", cc, dstadr), )
			if ncc != "F":
				x.a['flow'] += (( "cond", ncc, na),)
		if mne[-3:] == "JNZ":
			x.a['flow'] = (
			    ( "cond", "NZ", dstadr),
			    ( "cond", "Z", na),
			)

		if mne == "CALR":
			x.a['flow'] = ( ( "call", "T", dstadr), )
		if mne == "CALL":
			x.a['flow'] = ( ( "call", "T", dstadr), )
		if mne == "RET" and cc == "T":
			x.a['flow'] = ( ( "ret", "T", None), )

		if dstadr != None:
			x.a['DA'] = dstadr

		p.ins(x, self.disass)
