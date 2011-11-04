#!/usr/local/bin/python
#
# This is a demo-task which disassembles the CBM9000 boot EPROM
#
# XXX: BKP_Set: label is bogusly rendered
# XXX: cond_codes wrong, see 0:08b0
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
m0 = mem.byte_mem(0, 0x008000, 0, True, "big-endian")

m0.fromfile("EPROM_C_900_boot-H_V_1.0.bin", 0, 2)
m0.fromfile("EPROM_C_900_boot-L_V_1.0.bin", 1, 2)
m0.bcols=8

m1 = mem.byte_mem(0, 0x008000, 0, True, "big-endian")

m = mem.seg_mem(0x7f000000, 0x0000ffff)
m.add_seg(0, m0)
m.add_seg(1, m1)

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m)

print("%x" % p.lo, "%x" % p.hi)

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
# The data segment is copied from the EPROM to Segment 1

dseg_len = 0x1016
dseg_src = 0x6800

m1.setflags(0, dseg_len,
    m1.can_read|m1.can_write,
    m1.invalid|m1.undef)

for a in range(0, dseg_len):
	w = m0.rd(a + dseg_src)
	m1.wr(a, w)

x = p.t.add(m.linadr(0, dseg_src), m.linadr(0, dseg_src + dseg_len), "data_seg")
x.render = "[...]"
x.fold = True
x.blockcmt = """-
Data Segment Initializer data, moved to segment 1
"""

# XXX not sure how much this actually helps...
x = p.t.add(m.linadr(0, m0.start), m.linadr(0, m0.end), "Seg#0")
x = p.t.add(m.linadr(1, m1.start), m.linadr(1, m1.end), "Seg#1")

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

if True:
	x = const.txt(p, 0x0c76)
	const.txt(p, 0x010002a4)
	const.txt(p, 0x01000324)
	const.txt(p, 0x0100033b)
	const.txt(p, 0x01000352)
	const.txt(p, 0x01000554)
	const.txt(p, 0x0100056e)
	const.txt(p, 0x0100057e)
	const.txt(p, 0x01000592)
	const.txt(p, 0x010005ba)
	const.txt(p, 0x010005cb)
	const.txt(p, 0x010005e0)
	const.txt(p, 0x01000ea1)
		
#######################################################################
#

# Looks unref  INW(adr)
cpu.disass(0x0214)
p.setlabel(0x0214, "INW(adr)")

cpu.disass(0x22b0)

#######################################################################
#

x = p.t.add(0x4606, 0x6706, "Chargen")

if False:
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
else:
	x.fold = True
	x.render = "[...]"
	x.blockcmt = """-
Hi-Res Character Generator
"""

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
	q = dict()
	for i in range (0,l):
		const.w16(p, y + 2 * i)
		t = y + 2 * l + 4 * i
		idx = p.m.b16(y + 2 * i)
		res = p.m.b32(t)
		# XXX: should be .PTR
		x = const.w32(p, t)
		x.lcmt(" case %04x" % idx)
		z.flow("cond", "%d" % i, res)
		cpu.disass(res)
		q[idx]= res
	return q

###############
# Command-Switch main menu
q = caseW(0x0680)
p.setlabel(q[ord('(')], "MENU_BootSpec")
p.setlabel(q[ord('?')], "MENU_ShowMenu")
p.setlabel(q[ord('F')], "MENU_Floppy")
p.setlabel(q[ord('P')], "MENU_ParkDisk")
p.setlabel(q[ord('S')], "MENU_DiskParam")
p.setlabel(q[ord('d')], "MENU_Debugger")
p.setlabel(q[ord('l')], "MENU_LoadBoot")
p.setlabel(q[ord('m')], "MENU_ShowRam")

###############
# Command-Switch breakpoints
q = caseW(0x31a6)
p.setlabel(q[ord('c')], "BKP_Clear");
p.setlabel(q[ord('d')], "BKP_Display");
p.setlabel(q[ord('r')], "BKP_Remove");
p.setlabel(q[ord('s')], "BKP_Set");

###############
# Command-Switch debugger
q = caseW(0x3998)
p.setlabel(q[ord('?')], "DBG_Display_Help_Menu")
p.setlabel(q[ord('M')], "DBG_Display_MMU")
p.setlabel(q[ord('R')], "DBG_Modify_Register")
p.setlabel(q[ord('S')], "DBG_Remap_MMU")
p.setlabel(q[ord('a')], "DBG_Set_Base_Adr")
p.setlabel(q[ord('b')], "DBG_Breakpoints")
p.setlabel(q[ord('c')], "DBG_ContinueTrap")
p.setlabel(q[ord('e')], "DBG_EditMem")
p.setlabel(q[ord('f')], "DBG_FillMem")
p.setlabel(q[ord('h')], "DBG_HexMath")
p.setlabel(q[ord('i')], "DBG_Input")
p.setlabel(q[ord('m')], "DBG_MoveMem")
p.setlabel(q[ord('o')], "DBG_Output")
p.setlabel(q[ord('r')], "DBG_Registers")
p.setlabel(q[ord('s')], "DBG_Display_Stack")
p.setlabel(q[ord('t')], "DBG_t")

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

if True:
	for a in range(0x010005a0, 0x010005b8, 12):
		const.txtlen(p, a + 2, 2)
		const.w32(p, a + 4)
		cpu.disass(p.m.b32(a + 4))
		const.w32(p, a + 8)
		cpu.disass(p.m.b32(a + 8))

###############

x = p.t.add(0x7816,0x8000, "fill")
x.render = "ZFILL"
x.fold = True

x = p.t.add(0x6706,0x6800, "fill")
x.render = "ZFILL"
x.fold = True


#######################################################################
# Names

p.setlabel(0x020a, "INB(adr)")
p.setlabel(0x021c, "OUTB(adr,data)")
p.setlabel(0x0228, "OUTW(adr,data)")
p.setlabel(0x0234, "JMP(adr)")
p.setlabel(0x0274, "LDIRB(src,dst,len)")

p.setlabel(0x074c, "DiskParam(char *)")
p.setlabel(0x07d4, "ShowRam(void)")
p.setlabel(0x08b0, "int HexDigit(char *)")
p.setlabel(0x0900, "puts(char *)")
p.setlabel(0x0998, "ShowMenu(void)")
p.setlabel(0x09d8, "Floppy(char *)")
p.setlabel(0x0b26, "puthex(long val,int ndig)")
p.setlabel(0x0ac0, "ParkDisk(char *)")
p.setlabel(0x0fc2, "putchar(char)")

p.setlabel(0x20b8, "Debugger(void)")
p.setlabel(0x20e4, "AvidCHR(RL0,>R10)")
p.setlabel(0x4224, "BvidCHR(RL0,>R10)")
p.setlabel(0x21b6, "is_NL")
p.setlabel(0x2244, "is_CR")
p.setlabel(0x225e, "is_FF")
p.setlabel(0x226c, "is_BS")
p.setlabel(0x231e, "Debugger_Menu()")
p.setlabel(0x2bb6, "Debugger_MainLoop()")


p.setlabel(0x3b28, "OutStr(char*)")

#######################################################################

def txtptr(a):
	x = const.w32(p, a)
	w = const.txt(p, p.m.b32(a))
	w.fold = True
	x.lcmt('"' + w.txt + '"')

for a in range(0x01000006, 0x0100000e, 4):
	txtptr(a)
for a in range(0x01000010, 0x0100003c, 4):
	txtptr(a)
for a in range(0x01000618, 0x01000658, 4):
	txtptr(a)
for a in range(0x01000766, 0x010007AE, 4):
	txtptr(a)
for a in range(0x010007b4, 0x010007c4, 4):
	txtptr(a)
for a in range(0x01000c1a, 0x01000c26, 4):
	txtptr(a)

#######################################################################
# Disk-drive param settings
txtptr(0x0100003e)
txtptr(0x0100004c)
txtptr(0x0100005a)
txtptr(0x01000068)
#######################################################################

if True:
	for a in range(0x01000658, 0x01000705, 6):
		const.txtlen(p, a, 6)
		#const.w16(p, a)
		#const.w16(p, a + 2)
		#const.w16(p, a + 4)


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
	ta = p.m.b32(a - 6)
	try:
		w = const.txt(p, ta)
		w.fold = True
		t.lcmt('"' + w.txt + '"')
	except:
		print("%08x (%08x) failed" % (a, ta))
	return

p.t.recurse(Hunt_OutStr)

#######################################################################
# Build code graph

if True:
	p.g = topology.topology(p)
	p.g.build_bb()
	p.g.segment()
	p.g.setlabels(p)
	p.g.dump_dot()
	p.g.xxx(p)

#######################################################################
# Render output

print("Render")
r = render.render(p)
r.add_flows()
r.render("/tmp/_.cbm900.txt")
