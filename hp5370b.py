#!/usr/local/bin/python
#

from __future__ import print_function

import math

import mem
import array

import tree
import pyreveng

import cpu_mc6800

def render(p,start,end):
	while start < end:
		s = "%04x " % start
		t = ""
		b = start & ~15
		if p.m.tstflags(b, b + 16, p.m.undef):
			start = b + 16
			continue
		for i in range(0, start & 15):
			s += " .."
			t += "."
		for i in range(start & 15, 16):
			if b + i >= end:
				s += " .."
				t += "."
				continue
			try:
				x = p.m.rd(b + i)
			except:
				s += " --"
				t += "-"
				continue

			s += " %02x" % x
			if x >= 32 and x <= 126:
				t += "%c" % x
			else:
				t += "."
		s += "  |" + t + "|"
		print(s)
		start = b + 16

def foo(t, p, lvl):
	if t.seq == 0:
		return
	if t.tag == "gap":
		print("")
		render(p, t.start, t.end)
	elif t.tag == "ptr":
		print("%04x .ptr 0x%04x" % (t.start, p.m.b16(t.start)))
	elif t.tag == "str":
		s = "%04x .str '" % t.start
		for i in range(t.start, t.end):
			x = p.m.rd(i)
			if x < 32 or x > 126:
				s += "\\x%02x" % x
			else:
				s += "%c" % x
		s += "'"
		print(s)
	elif t.tag == "ins":
		s = "%04x " % t.start
		if t.start in p.bbstart:
			s += "{"
		if t.start in p.bbend:
			s += "}"
		s += " "
		for i in range(t.start, t.end):
			s += "%02x" % p.m.rd(i)
		s += "                                  "
		s = s[0:24 + lvl * 2]
		s += t.a['mne']
		s += "\t"
		s += ",".join(t.a['op'])
		print(s)
	elif t.tag == "run":
		print("\n%04x-%04x %s" % (t.start, t.end, t.tag))
	else:
		print("%04x-%04x %s" % (t.start, t.end, t.tag))
		render(p, t.start, t.end)

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

		

if __name__ == "__main__":

	def ptr(p,x):
		p.t.add(x,x+2,"ptr")
		p.todo(p.m.b16(x), p.cpu.disass)
		
	def str(p,x,l):
		p.t.add(x,x+l,"str")
		

	dn="/rdonly/Doc/TestAndMeasurement/HP5370B/Firmware/"

	p = pyreveng.pyreveng(mem.byte_mem(0, 0x10000, 0, True))
	p.m.fromfile(dn + "HP5370B.ROM", 0x7fff, -1)

	# 0x6f00...0x7000 = x^2/256 table

	f = open("/tmp/_x", "w")
	for a in range(0x6f00,0x7000):
		f.write("%d\n" % p.m.rd(a))
	f.close()

	print(nbr_render(p, 0x614c))
	print(nbr_render(p, 0x619c))
	print(nbr_render(p, 0x61a3))
	print(nbr_render(p, 0x69dd))
	print(nbr_render(p, 0x69e4))
	print("")
	for a in range(0x6e00,0x6f00,8):
		print(nbr_render(p, a))
	exit(0)

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
	str(p,0x78f3,4)
	str(p,0x78f7,6)
	str(p,0x78fd,2)
	for i in range(0x77d7,0x77f7,4):
		str(p,i,4)
	for i in range(0x7c64,0x7c98,2):
		str(p,i,2)
		
	while p.run():
		#study(p)
		pass
	print(p.t.gaps())
	for g in p.t.gaps():
		p.t.add(g[0], g[1], "gap")
	p.t.recurse(foo, p)
	p.t.recurse()

