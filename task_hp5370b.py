#!/usr/local/bin/python
#

from __future__ import print_function

import math

import mem
import array

import tree
import pyreveng

import cpu_mc6800

procat=dict()

def sdisc(p, tg):
	print(tg)
	print("Discover %04x" % tg)
	te = tg
	while True:
		x = p.t.find(te, None, "func")
		if x != None:
			print("FALL INTO", tg, x)
			te = x.end
			break
		x = p.t.find(te, None, "ins")
		if x == None:
			break
		if x.start == tg and 'jmp' in x.a:
			print("CALL TO JUMP", x)
			tg = x.a['jmp'][0]
			if tg != None and tg not in procat:
				procat[tg] = True
				sdisc(p,tg)
			return
		print("%04x-%04x %s %s" % (x.start, x.end, x.a['mne'], str(x.a['op'])))
		te = x.end
		if 'ret' in x.a:
			break
	print("Found %04x...%04x" % (tg,te))
	if tg != te:
		p.t.add(tg, te, "func")

def sfunc(t,p,lvl):
	if not 'call' in t.a:
		return
	for tg in t.a['call']:
		if tg == None:
			continue
		if tg in procat:
			continue
		procat[tg] = True
		sdisc(p,tg)

def study(p):
	p.t.recurse(sfunc, p)

# HP5370B uses its own weird floating point format
def nbr_render(p, a):
	x = p.m.rd(a + 0)
	if x & 0x80:
		s = -1
		x ^= 0x80
	else:
		s = 1
	m =  x * 1099511627776.
	m += p.m.rd(a + 1) * 4294967296.
	m += p.m.rd(a + 2) * 16777216.
	m += p.m.rd(a + 3) * 65536.
	m += p.m.rd(a + 4) * 256.
	m += p.m.rd(a + 5)
	e =  p.m.s8(a + 6)
	v = m / (math.pow(2, 17-e) * math.pow(10, 8))
	#x = "m %f" % m + " e %d" % e + " v %g" % v
	x = "%.9e" % v
	if x.find(".") == -1 and x.find("e") == -1:
		x = x + "."
	return x

class dot_ascii(tree.tree):
	def __init__(self, p, adr, len):
		tree.tree.__init__(self, adr, adr + len, "dot-ascii")
		p.t.add(adr, adr + 1, "dot-ascii", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'"
		for i in range(t.start, t.end):
			x = p.m.rd(i)
			s += mem.ascii(x)
		s += "'"
		return (s,)

class dot_code(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 2, "dot-code")
		p.t.add(adr, adr + 2, "dot-code", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".CODE\t%04x" % p.m.b16(t.start)
		return (s,)

class dot_float(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 7, "dot_float")
		p.t.add(adr, adr + 7, "dot-float", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".FLOAT\t%s" % nbr_render(p, t.start)
		return (s,)

if __name__ == "__main__":

	def ptr(p,x):
		dot_code(p, x)
		p.todo(p.m.b16(x), p.cpu.disass)
		
	dn="/rdonly/Doc/TestAndMeasurement/HP5370B/Firmware/"


	m = mem.byte_mem(0, 0x10000, 0, True)
	p = pyreveng.pyreveng(m)
	p.m.fromfile(dn + "HP5370B.ROM", 0x7fff, -1)

	# 0x6f00...0x7000 = x^2/256 table

	dot_float(p, 0x614c)
	dot_float(p, 0x619c)
	dot_float(p, 0x61a3)
	dot_float(p, 0x69dd)
	dot_float(p, 0x69e4)

	p.cpu = cpu_mc6800.mc6800()
	p.t.recurse()

	for i in range(0x6000,0x8000,0x400):
		p.t.add(i, i + 3, "checksum")
	
	ptr(p, 0x7ffe)
	ptr(p, 0x7ffc)
	ptr(p, 0x7ffa)
	ptr(p, 0x7ff8)

	# jmp table, see 7962->6054->63ec
	#ptr(p, 0x6403)
	for i in range(0x640c,0x644c,2):
		ptr(p, i)
	#ptr(p, 0x6405)
	for i in range(0x644c,0x64ac,2):
		ptr(p, i)
	#ptr(p, 0x6407)
	for i in range(0x64ac,0x64c4,2):
		ptr(p, i)
	# jmp table
	for i in range(0x6848,0x6858,2):
		ptr(p, i)

	# strings
	dot_ascii(p,0x78f3,4)
	dot_ascii(p,0x78f7,6)
	dot_ascii(p,0x78fd,2)
	for i in range(0x77d7,0x77f7,4):
		dot_ascii(p,i,4)
	for i in range(0x7c64,0x7c98,2):
		dot_ascii(p,i,2)
		
	while p.run():
		#study(p)
		pass
	p.render()
