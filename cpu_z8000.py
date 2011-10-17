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

class z8000(object):
	def __init__(self):
		self.dummy = True
		self.al = 2
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
		# print("RA", "%04x" % adr, arg, "%04x" % i)
		return i

	def get_reg(self, p, adr, arg, c, w = None):
		if w == None:
			w = 1
			if "W" in c:
				w = self.rdarg(p, adr, c["W"])
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
			return None
		if w:
			return "R%d" % v
		if v & 8:
			return "RL%d" % (v & 7)
		else:
			return "RH%d" % (v & 7)

	def disass(self, p, adr, priv = None):
		if p.t.find(adr, "ins") != None:
			return
		try:
			iw = p.m.b16(adr)
			iw2 = p.m.rd(adr + 2)
		except:
			print("FETCH failed:", adr)
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
		print(">>>", c)
		x = p.t.add(adr, adr + (c[1] >> 3), "ins")
		x.a['mne'] = c[2]
		ol = list()
		for i in c[3]:
			y = i
			if i == "FCW":
				pass
			elif i == "Rd":
				i = self.get_reg(p, adr, "Rd", c[4])
			elif i == "@Rd":
				i = "@" + self.get_reg(p, adr, "Rd", c[4], w = 1)
			elif i == "Rbd":
				i = self.get_reg(p, adr, "Rbd", c[4], w = 0)
			elif i == "Rs":
				i = self.get_reg(p, adr, "Rs", c[4])
			elif i == "@Rs":
				i = "@" + self.get_reg(p, adr, "Rs", c[4], w = 1)
			elif i == "address":
				if "address" in c[4]:
					j = self.rdarg(p, adr, c[4]["address"])
					if j & 0x8000:
						print("Error: Long segment address %04x" % j)
					i = "0x%04x" % j
			elif i == "addr(Rs)":
				r = self.get_reg(p, adr, "Rs", c[4], w = 1)
				j = self.rdarg(p, adr, c[4]["address"])
				if j & 0x8000:
					print("Error: High bit set in <address> %04x" % j)
					return
				i = "%04x(%s)" % (j, r)
			elif i == "#data":
				# XXX: 8-bit data
				j = self.rdarg(p, adr, c[4]["data"])
				i = "#%04x" % j
			elif i == "port":
				j = self.rdarg(p, adr, c[4]["port"])
				i = "%04x" % j
			elif i == "#b":
				# XXX: negative shifts modify mne
				j = self.rdarg(p, adr, c[4]["b"])
				i = "%d" % j
			else:
				print(y, "???", i)
			if y != i:
				print(y, "-->", i)
			ol.append(i)
			
		x.a['oper'] = ol
		x.render = self.render
		p.todo(adr + (c[1] >> 3), self.disass)
		print()
