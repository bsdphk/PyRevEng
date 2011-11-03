#!/usr/local/bin/python
#
# This is a demo-task which disassembles the CBM9000 boot EPROM
#

#######################################################################
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#######################################################################
# Set up a search path to two levels below

import os
sys.path.insert(0, os.path.abspath(os.path.join(".", "..", "..")))

#######################################################################
# Stuff we need...
import mem
import const
import pyreveng
import render
import topology
import cpus.z8000


#######################################################################
# Set up the memory image
m = mem.byte_mem(0, 0x008000, 0, True, "big-endian")

m.fromfile("EPROM_C_900_boot-H_V_1.0.bin", 0, 2)
m.fromfile("EPROM_C_900_boot-L_V_1.0.bin", 1, 2)
m.bcols=8

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m)

#######################################################################
# Instantiate a disassembler
cpu = cpus.z8000.z8000(p, segmented = True)

#######################################################################
# Provide hints for disassembly
# const.w16(p, 0)
x = const.w16(p, 2)
x.lcmt("Reset PSW")
x = const.w16(p, 4)
x.lcmt("Reset SEG")
x = const.w16(p, 6)
x.lcmt("Reset PC")

p.setlabel(p.m.b16(6), "RESET")
cpu.disass(p.m.b16(6))
cpu.disass(0)

#######################################################################
#
x = p.t.add(0x0000, 0x020a, "section")
x.blockcmt += """-
First section, Vectors, Reset, Setup Segments
"""

p.setlabel(0x0326, "ResetHandler")

#######################################################################
#
x = p.t.add(0x020a, 0x0326, "section")
x.blockcmt += """-
Second section, Assy support for C-code, runs in C-env
"""

p.setlabel(0x2040, "TrapHandler")

#######################################################################
# More hints...

if True:
	# non-stack calls LDA RR10,0x??:0x????
	cpu.disass(0x0c0a)
	cpu.disass(0x01c0)
	cpu.disass(0x0c44)
	cpu.disass(0x0e9e)
	cpu.disass(0x0eae)
	cpu.disass(0x0ee0)
	cpu.disass(0x0ef0)
	cpu.disass(0x20bc)
	cpu.disass(0x3ec6)
	cpu.disass(0x3eca)

if False:
	const.txt(p, 0x0c76)
	const.txt(p, 0x6876)
	const.txt(p, 0x6885)
	const.txt(p, 0x6892)
	const.txt(p, 0x68ab)
	const.txt(p, 0x68e6)
	const.txt(p, 0x691f)
	const.txt(p, 0x695a)
	const.txt(p, 0x761e)
	const.txt(p, 0x7629)
		
#######################################################################
#

# Looks unref  INW(adr)
cpu.disass(0x0214)
p.setlabel(0x0214, "INW(adr)")

cpu.disass(0x22b0)

def chargen(adr):
	const.byte(p,adr)
	const.byte(p,adr + 1)
	for j in range(2, 66, 2):
		x = const.w16(p, adr + j)
		y = p.m.b16(adr + j)
		s = ""
		for b in range(15, -1, -1):
			if y & (1 << b):
				s += "#"
			else:
				s += "."
		x.lcmt(s)
	

for a in range(0x4606, 0x6700,66):
	chargen(a)

###############
for a in range(0x3e90, 0x3ea0, 4):
	const.w32(p, a)
	cpu.disass(p.m.b32(a))

###############
def caseW(a):
	x = p.m.b32(a)
	assert (x >> 16) == 0x2100
	l = x & 0xffff
	y = p.m.b16(a + 4)
	assert y == 0x1402
	y = p.m.b32(a + 6)
	z = p.m.b16(y - 2)
	assert z == 0x1e28
	z = cpu.disass(y - 2)
	print("CASE", "l=%d" % l, "y=%x" % y)
	for i in range (0,l):
		const.w16(p, y + 2 * i)
		t = y + 2 * l + 4 * i
		const.w32(p, t)
		z.flow("cond", "%d" % i, p.m.b32(t))
		cpu.disass(p.m.b32(t))

caseW(0x0680)
caseW(0x31a6)
caseW(0x3998)
###############
for a in range(0x419e, 0x4202, 4):
	const.w32(p, a)
	cpu.disass(p.m.b32(a))
###############

v = (
	"Extended Instruction",
	"Privileged Instruction",
	"System Call",
	"Segment",
	"NMI",
	"Non-Vector IRQ",
)
for a in range(0x0008,0x0038, 8):
	const.w32(p, a)
	x = const.w32(p, a + 4)
	x.lcmt(v[0])
	y = p.m.b16(a + 6)
	cpu.disass(y)
	p.setlabel(y, v[0])
	v = v[1:]

###############

for a in range(0x6da0, 0x6db8, 12):
	const.txtlen(p, a + 2, 2)
	const.w32(p, a + 4)
	cpu.disass(p.m.b32(a + 4))
	const.w32(p, a + 8)
	cpu.disass(p.m.b32(a + 8))

###############

x = p.t.add(0x7816,0x8000, "fill")
x.render = "ZFILL"


#######################################################################
# Names

p.setlabel(0x020a, "INB(adr)")
p.setlabel(0x021c, "OUTB(adr,data)")
p.setlabel(0x0228, "OUTW(adr,data)")
p.setlabel(0x0234, "JMP(adr)")
p.setlabel(0x0274, "LDIRB(src,dst,len)")

p.setlabel(0x20e4, "AvidCHR(RL0,>R10)")
p.setlabel(0x4224, "BvidCHR(RL0,>R10)")
p.setlabel(0x21b6, "is_NL")
p.setlabel(0x2244, "is_CR")
p.setlabel(0x225e, "is_FF")
p.setlabel(0x226c, "is_BS")

p.setlabel(0x3b28, "OutStr(char*)")

#######################################################################

def txtptr(a):
	x = const.w32(p, a)
	y = p.m.b16(a + 2)
	y += 0x6800
	w = const.txt(p, y)
	x.lcmt('"' + w.txt + '"')

for a in range(0x6e18, 0x6e58, 4):
	txtptr(a)
for a in range(0x6f66, 0x6fae, 4):
	txtptr(a)
for a in range(0x6fb4, 0x6fc4, 4):
	txtptr(a)
for a in range(0x741a, 0x7426, 4):
	txtptr(a)

#######################################################################

for a in range(0x6e58, 0x6f05, 6):
	const.w16(p, a)
	const.w16(p, a + 2)
	const.w16(p, a + 4)


#######################################################################
# Chew through what we got

while p.run():
	pass

cpu.to_tree()

#######################################################################

print("Hunt OutStr() calls")

def Hunt_OutStr(t, priv, lvl):
	a = t.start
	if p.m.b16(a) != 0x5f00:
		return
	d = p.m.b32(a + 2)
	if d != 0x80003b28 and d != 0x80000900: 
		return
	if p.m.b16(a - 2) != 0x91e0:
		return
	if p.m.b16(a - 8) != 0x1400:
		return
	x = p.m.b16(a - 6)
	y = p.m.b16(a - 4)
	if x != 0x0100:
		return
	try:
		w = const.txt(p, 0x6800 + y)
		t.lcmt('"' + w.txt + '"')
	except:
		print("%04x failed" % a)
		print(t, "%04x:" % a, "%04x" % y )

p.t.recurse(Hunt_OutStr)

#######################################################################
# Build code graph

if True:
	p.g = topology.topology(p)
	p.g.build_bb()
	p.g.segment()
	p.g.dump_dot()
	p.g.xxx(p)

#######################################################################
# Render output

print("Render")
r = render.render(p)
r.add_flows()
r.render("/tmp/_.cbm900.txt")
