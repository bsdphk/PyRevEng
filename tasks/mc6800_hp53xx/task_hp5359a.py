#!/usr/local/bin/python
#
# This is a "real" task which disassembles the MC6800 ROM from a
# Hewlett Packard HP5359A Time Synthesizer
#
# For a good introduction to this instrument see:
#     http://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1978-08.pdf
#
# This is a pretty comprehensive disassembly, which shows off some of
# the strengths of PyRevEng
#
# Stuff is shared with the disassembly of the HP5359A sister instrument

#----------------------------------------------------------------------
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#----------------------------------------------------------------------
# Set up a search path to two levels below

import os
sys.path.insert(0, os.path.abspath(os.path.join(".", "..", "..")))

#----------------------------------------------------------------------
# Stuff we need...

# Python classes
import math

# PyRevEng classes
import mem
import tree
import const
import pyreveng
import cpus.mc6800
import topology

# Local classes
import hp53xx

#----------------------------------------------------------------------
# Set up the memory image

m = mem.byte_mem(0, 0x10000, 0, True, "big-endian")
m.fromfile("HP5359A.ROM", 0x6000, 1)
m.bcols = 3

#----------------------------------------------------------------------
# Create a pyreveng instance

p = pyreveng.pyreveng(m)

#----------------------------------------------------------------------
# Add a CPU instance
#

cpu = cpus.mc6800.mc6800(p)
cpu.vectors(0x8000)

#----------------------------------------------------------------------
# HP53xx EPROM structure
hp53xx.eprom(p, cpu.disass, 0x6000, 0x8000, 0x400)
#----------------------------------------------------------------------

for a in range(0x7fbf, 0x7fda):
	const.seven_segment(p, a)
p.setlabel(0x7fbf, "CHARGEN")

#----------------------------------------------------------------------
hp53xx.wr_test_val(p)

const.fill(p, hi=0x63ff)
const.fill(p, hi=0x67ff)
const.fill(p, hi=0x68ff)
const.fill(p, hi=0x6bff)
const.fill(p, hi=0x6fff)
const.fill(p, hi=0x73ff)
const.fill(p, hi=0x77ff)
const.fill(p, hi=0x7bff)
const.fill(p, hi=0x7eff)
const.fill(p, hi=0x7ff7)
#----------------------------------------------------------------------


# See 0x61a4
cpu.disass(0x6175)
# See 0x61fa
cpu.disass(0x616b)
cpu.disass(0x60a1)

const.w16(p, 0x68b7)
#----------------------------------------------------------------------
while p.run():
	pass

#----------------------------------------------------------------------
hp53xx.nmi_debugger(p, cpu)
#----------------------------------------------------------------------
hp5359_cmds = {
	"F":	"Frequency Mode",
	"P":	"Period Mode",
	"D":	"Delay",
	"W":	"Width",
	"SS":	"Step Size",
	"SU":	"Step Up",
	"SD":	"Step Down",
	"EN":	"Events Slope Negative",
	"EP":	"Events Slope Positive",
	"TP":	"External Trigger Positive Slope",
	"TN":	"External Trigger Negative Slope",
	"TM":	"Trigger Manual",
	"ID":	"Trigger Input Disable",
	"IE":	"Trigger Input Enable",
	"TF":	"Triggered Frequency On",
	"NF":	"Normal Frequency",
	"ON":	"Output Normal",
	"OC":	"Output Complement",
	"OA":	"Output Amplitude",
	"OO":	"Output Offset",
	"OL":	"Output Local",
	"SC":	"Single Cycle",
	"RA":	"Rearm",
	"NC":	"Normal Cycle",
	"OD":	"Output Disable",
	"OE":	"Output Enable",
	"SP":	"Sync Delay-Preset",
	"SA":	"Sync Delay-Auto",
	"C":	"Calibrate",
	"EC":	"External Compensation",
	"aE":	"External Compensation Enable",
	"aD":	"External Compensation Disable",
	"TE":	"Teach",
	"LN":	"Learn",
}

#----------------------------------------------------------------------

def hp5359_nbr(p, data):
	assert len(data) == 8
	m = 0.0
	for ax in range(6, 0, -1):
		w = data[ax]
		m *= .1
		m += w & 0xf
		m *= .1
		m += w >> 4
	m *= .1

	e = data[7]
	if e >= 128:
		e -= 256
	if data[0] == 0x90:
		m *= -1.
	elif data[0] == 0x00:
		pass
	else:
		assert data[0] == 0
	
	return "%.12fE%d" % (m,e)

if False:
	b=bytearray()
	fp = hp5359_nbr(p, b.fromhex("00456700000000fe"))
	fp = hp5359_nbr(p, b.fromhex("00123400000000ff"))
	fp = hp5359_nbr(p, b.fromhex("0010000000000004"))
	e = float(fp)
	print(fp, e)
	exit(0)

class dot_float(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 8, "dot_float")
		p.t.add(self.start, self.end, self.tag, True, self)
		self.render = self.rfunc
		b = bytearray()
		for i in range(0,8):
			b.append(p.m.rd(adr + i))
		self.nbr = hp5359_nbr(p, b)
		self.a['const'] = "FLOAT=%e" % float(self.nbr)
		p.setlabel(adr, self.a['const'])

	def rfunc(self, p, t):
		s = ".FLOAT\t%e" % float(self.nbr)
		return (s,)

#----------------------------------------------------------------------
for i in range(0x7f03, 0x7fa3, 8):
	dot_float(p, i)
#----------------------------------------------------------------------
const.byte(p, 0x7fa3, 7)
const.byte(p, 0x7faa, 7)
const.byte(p, 0x7fb1, 7)
const.byte(p, 0x7fb8, 7)
#----------------------------------------------------------------------
for ax in range(0x6225,0x6287,2):
	x = const.txtlen(p, ax, 2)
	if ax < 0x624d:
		continue
	a2 = ax - 0x624d + 0x6287
	y = p.m.b16(a2)
	tt = x.txt
	if tt[1:] == "\\x00":
		tt = tt[:1]
	if tt[0] == "a":
		tt = "EC" + tt[1:]
	print("%04x" % ax, "%04x" % a2, "%04x" % y, tt)
	p.setlabel(y, "CMD_" + tt)
x = p.t.add(0x6225,0x6287, "tbl")
p.setlabel(0x6225, "CMD_TABLE")

#----------------------------------------------------------------------
for i in range(0x6287, 0x62c1,2):
	y = p.m.b16(i)
	if y not in p.label:
		p.setlabel(y, "CMD_%04x" % y)
#----------------------------------------------------------------------
p.setlabel(0x6a4e, "MAIN_LOOP")
#----------------------------------------------------------------------

# Based on service manual p.8-100
# Note that cols are unsorted in diagram
hp5359_keys = (
    ("Width",  "Cal",    "7", "8",	 "9",	 "ns",	 "Local_Remote", ""),
    ("Delay",  "StepUp", "4", "5",	 "6",	 "us",	 "Man_Trig",     ""),
    ("Period", "StepDn", "1", "2",	 "3",	 "ms",	 "",             ""),
    ("Freq",   "StepSz", "0", "dot", "Clear", "EVT", "Disp_Level",       ""),
)

for row in range(0,4):
	for col in range(0,8):
		a = 0x703d + 2 * row + 8 * col
		y = p.m.b16(a)
		n = hp5359_keys[row][7-col]
		if n == "":
			n = "invalid"
		p.setlabel(y, "KEY_" + n)

		# Service mode keys, see 0x7ba
		a += 18
		if a > 0x707b and a < 0x708f:
			y = p.m.b16(a)
			p.setlabel(y, "KEY_SRV_" + n)


for i in range(0x703d, 0x708f,2):
	y = p.m.b16(i)
	if y not in p.label:
		p.setlabel(y, "KEY_%04x" % y)
#----------------------------------------------------------------------


def jmptbl(p, jmp, low, high, name, flow="call"):
	x = p.t.add(low, high, "tbl")
	print("Call table for", name)
	ins = cpu.ins[jmp]
	for i in range(low, high, 2):
		const.ptr(p, i)
		y = p.m.b16(i)
		ins.flow(flow, name, y)
		cpu.disass(y)

jmptbl(p, 0x6223, 0x6287, 0x62c1, "HPIBCMD", "cond")
jmptbl(p, 0x703b, 0x703d, 0x708f, "KEYCMD", "cond")
#----------------------------------------------------------------------
while p.run():
	pass
#----------------------------------------------------------------------

if True:
	# SWI calls whatever is in the X register
	ins = cpu.ins[0x7422]
	ins.flow("call", "SWI", 0x7018)
	cpu.disass(0x7018)

	ins = cpu.ins[0x60a0]
	ins.flow("call", "SWI", 0x6355)
	cpu.disass(0x6355)

#----------------------------------------------------------------------

if True:
	# Calls through 0x016d
	# @ 61a7 -> 6175
	# @ 61fa -> 616b
	# @ 61ff -> 6175
	# @ 6f83 -> 6009
	# @ 73ef -> 6009
	ins = cpu.ins[0x6169]
	ins.flow("cond", "T", 0x6175)
	ins.flow("cond", "T", 0x616b)

#----------------------------------------------------------------------
p.setlabel(0x7c26, "ram_0x00_fill")
p.setlabel(0x7c33, "ram_0x00_check")
p.setlabel(0x7c41, "ram_shift_test")
p.setlabel(0x7d75, "lamp_test")
p.setlabel(0x7cac, "rom_test_loop")
p.setlabel(0x7cd9, "rom_csum_loop")
p.setlabel(0x6c39, "STARTUP")
p.setlabel(0x6fa3, "init_numbers")
p.setlabel(0x6fc5, "reset_numbers")

#----------------------------------------------------------------------
p.setlabel(0x72f1, "LED=Err(A)")
p.setlabel(0x6670, "(X).m /= 10")
p.setlabel(0x668a, "(X).m *= 10")
p.setlabel(0x7394, "A=(X+A)")
p.setlabel(0x6006, "HPIB_SEND(*X,A)")
p.setlabel(0x6123, "HPIB_RECV(*X,A,B=nowait)")
p.setlabel(0x6184, "CR?")
p.setlabel(0x6188, "NL?")
p.setlabel(0x618c, "SP?")
p.setlabel(0x6190, "PLUS?")
p.setlabel(0x61b2, "TOLOWER")
p.setlabel(0x61fa, "GETMORECHARS")
p.setlabel(0x7ef2, 'Err(2.0=Range)')
p.setlabel(0x6ff1, 'Err(2.0=Range)')
p.setlabel(0x7a81, 'Err(3.0=Ill_Cmd)')
p.setlabel(0x6aca, 'Err(3.0=Ill_Cmd)')
p.setlabel(0x6a98, 'Err(4.0=PLL_unlock)')
p.setlabel(0x7403, 'Calibrate()')
p.setlabel(0x7030, "KEY_CMD(A)")
p.setlabel(0x6a0f, "Num->SX()")
p.setlabel(0x7226, "RANGE_ERROR")

p.setlabel(0x7803, "RANGE_CHECK0(0.1e-8)")
p.setlabel(0x780c, "RANGE_CHECK1(0.5e-8)")
p.setlabel(0x780f, "RANGE_CHECK2(0.1e-7)")
p.setlabel(0x7806, "RANGE_CHECK3(0.6e1)")
p.setlabel(0x781b, "RANGE_CHECK4")
p.setlabel(0x7a23, "z_return")
p.setlabel(0x7a28, "nz_return")

p.setlabel(0x72c8, "X=stepsize(A)")

p.setlabel(0x64b9, "DROPSY()")
p.setlabel(0x6641, "SX.m==0?")
p.setlabel(0x6415, "ADD")
p.setlabel(0x6418, "SUBTRACT")
p.hint(0x64de)['dot-page'] = "rankdir=LR"
p.setlabel(0x6535, "FP_ALIGN()")
p.setlabel(0x664e, "DIGIT_SHIFT_RIGHT()")

p.setlabel(0x7ad2, "DisplayLevels()")


p.setlabel(0x64c8, "SX=0.0")
p.setlabel(0x64cb, "SX.m=0.0")
p.setlabel(0x64d7, "SX=-SX")

p.setlabel(0x6511, "SX.m+=SY.m")

p.setlabel(0x6477, "EXCH()")
p.setlabel(0x64ab, "DROP()")

p.setlabel(0x6486, "DUP()")
p.hint(0x6486)['dot-page'] = "rankdir=LR"

p.setlabel(0x6456, "(X)=SX")
p.hint(0x6456)['dot-page'] = "rankdir=LR"

p.setlabel(0x6442, "PUSH(?X)")
p.hint(0x6442)['dot-page'] = "rankdir=LR"

p.setlabel(0x6dc3, "DELAY(X)")
p.hint(0x6dc3)['dot-page'] = "rankdir=LR"

p.hint(0x7027)['dot-page'] = "rankdir=LR"

p.hint(0x6b29)['dot-page'] = "rankdir=LR"
#----------------------------------------------------------------------
p.setlabel(0x7c03, "UpdateNumber(B)")

#----------------------------------------------------------------------
cpu.to_tree()

#----------------------------------------------------------------------
if False:
	fo = open("/tmp/_", "w")
	for i in cpu.ins:
		fo.write(cpu.ins[i].debug() + "\n")
	fo.close()
	exit(0)
#----------------------------------------------------------------------

p.g = topology.topology(p)
p.g.build_bb()

p.g.findflow(0x73bf,0x73f7).offpage = True
p.g.findflow(0x73c9,0x73f7).offpage = True

p.g.findflow(0x61ff,0x6216).offpage = True
for i in p.g.bbs[0x6216].flow_out:
	i.offpage = True
p.hint(0x6216)['dot-page'] = "rankdir=LR"
p.setlabel(0x6216, "HPIB_CMD()")

for i in p.g.bbs[0x6338].flow_in:
	i.offpage = True

p.g.segment()
p.g.setlabels(p)
p.g.dump_dot()

p.g.xxx(p)

#----------------------------------------------------------------------

import render
r = render.render(p)

r.add_flows()

r.render("/tmp/_.hp5359a.txt")
exit(0)

#----------------------------------------------------------------------
# Old junk, kept for information purposes

if False:


	p.t.blockcmt += """-
	HP5359A ROM disassembly
	=======================

	"""

	hp53xx.gpib_board(p)
	hp53xx.display_board(p)

	p.t.blockcmt += """-
	0x0010-0x002f PROCESSOR INTERFACE (A16)

		0x0011:R
			x x 0 0 x x x x 	read/write/loop test mode
			x x 0 1 x x x x 	read/loop test mode
			0x10	Service switch (?)
			0x20	Service switch (?)
			0x30
			0x04	@ 6a94  PLL-unlock ?

		(from p3-5:)
		Err 1:		Illegal Remote Command or an undefined function
		Err 2:		Data out of range
		Err 3:		Illegal key combination (local of HP-IB)
		Err 4:		Phase-locked-loop out of lock
		Err 5:		Undefined Key (hardware problem)
		Err 6.n:	RAM error
		Err 7.n:	ROM error
		Err 7.9:	ROM missing
		Probe Err 8.n:	Unable to calibrate using external probes
		Err 9.n:	Calibrate error
	"""

	p.t.blockcmt += """-
	0x0080-0x0200	RAM

		0x0080-0x0087	SW	X X X X X X X X
		0x0088-0x008f	SZ	X X X X X X X X
		0x0090-0x0097	SY	m m m m m m m X
		0x0098-0x009f	SX	m m m m m m m X
		0x00a0-0x00a7	SA	X X X X X X X X

		0x00cf		number input pointer
		0x00d0		number input decimal position
		0x00d1-...	number input buffer

		0x00e2-0x0123	TEach/LearN data
				0x00e2	X		0x0012 copy
					0x20 - Output Enable
				0x00e3	X		0x0014 copy
					0x10 - Output Remote(!local)
				0x00e4	X		0x0016 copy
					0x04 - Output Polarity (0 = Complement)
					0x20 - Extern Trig Slope (1 = Positive)
					0x40 - Events Slope (1 = Negative)
					0x80 - Single Cycle
				0x00e5	X
					0x01 @ 61ae
					0x04 - Output Amplitude
					0x08 - Output Offset
					0x80 - input 'E' seen (@62ca)
					0x20 - input '-' seen (@62e9)
					0xc0 - input '-' seen (@62f2)
				0x00e6	m m m m m m m e
					period
					1e-6 in reset_numbers()
				0x00ee	m m m m m m m e
					pulse width
					1e-7 in reset_numbers()
				0x00f6	X
					0x01 - External Compensation Enable
					0x80 - Sync Delay Preset
				0x00f7	X
				0x00f8	X
					0x01 = digit seen ?
					0x02 = dot seen ?
					0x01 @61bc
					0x01 @62c3
					0x01 @62e3
					0x04 @6fe4 (Key_Clear)
				0x00f9	X
					0x80 - Frequency
					0x40 - Width
					0x20 - Delay
					0x10 - Period
				0x00fa	X
				0x00fb	X
				0x00fc	X X
				0x00fe
					0x50 in reset_numbers()
				0x00ff  m m m m m m m e
					Step size ?
					1e-9 in init_numbers()
				0x0107  m m m m m m m e
					Step size ?
					1e-9 in init_numbers()
				0x010f  m m m m m m m e
					Step size ?
					1e-9 in init_numbers()
				0x0117  m m m m m m m e
					Step size (Freq) ?
					1000 in init_numbers()
				0x011f	X X X
				0x0122	X 		0x002e copy
				0x0123	X 		0x002c copy

		0x013c-0x0143		m m m m m m m e
		0x0144-0x014b		m m m m m m m e
		0x014c-0x0153		m m m m m m m e
		0x0154-0x015b		m m m m m m m e
		0x015c-0x0163		m m m m m m m e

		0x0164-0x0165	Points to struct 		@7fa3	@7fb1
				----------------------------------------------
				[0x00-0x01]	LDX		0x013c	0x0144
				[0x02-0x03]	LDX		0x0154	0x014c
				[0x04-0x05]	LDX STA->	0x001a	0x0018
				[0x06]		EOR		0x00	0x90
				[0x07-0x08]	LDX		0x0144	0x013c
				[0x09-0x0a]	LDX		0x014c	0x0154
				[0x0b-0x0c]	LDX		0x0018	0x001a
				[0x0d]				0x02	0x04

		0x0167		HPIB_TX_LEN
		0x0168-0x0169	HPIB_RX_PTR
		0x016a		HPIB_RX_LEN
		0x016b-0x016c	HPIB_RX_PTR
		0x016d-0x016e	HPIB_RX_FUNC

		0x016f-		HPIB_CMD_BUF

		0x0175		HPIB.STATUS_OUT copy (=spoll))
		0x0176		@6aac


	"""

	#----------------------------------------------------------------------
	def ea(p,adr):
		adr = p.m.w16(adr)
		while True:
			if p.m.rd(adr) != 0x7e:
				return adr
			adr = p.m.w16(adr + 1)

	#----------------------------------------------------------------------
	p.setlabel(0x0098, "SX.m")
	p.setlabel(0x009f, "SX.e")
	p.setlabel(0x00e4, "COPY_16")
	p.setlabel(0x0122, "COPY_2E")
	p.setlabel(0x0123, "COPY_2C")
	p.setlabel(0x0167, "HPIB_TX_LEN")
	p.setlabel(0x0168, "HPIB_TX_PTR")
	p.setlabel(0x016a, "HPIB_TX_LEN")
	p.setlabel(0x016b, "HPIB_TX_PTR")

	cpu.disass(0x616b)
	p.setlabel(0x016b, "HPIB_RX_FUNC1")
	p.setlabel(0x016d, "HPIB_RX_FUNC")


	#----------------------------------------------------------------------
	p.setlabel(0x6175, "RX_HPIB()")
	p.setlabel(0x6216, "HPIBCMD(0x14+)")
	p.setlabel(0x6463, "memcpy(0x00c5,0x00c3,8)")
	p.setlabel(0x6465, "memcpy(0x00c5,0x00c3,B)")
	p.setlabel(0x649c, "SY=SX")
	p.setlabel(0x64b9, "SY=SZ,SZ=SW")
	p.setlabel(0x6641, "A=OR(SX.m)")
	p.setlabel(0x6f72, "START_UP()")
	p.setlabel(0x6ff1, "Err2_Data_Out_Of_Range()")
	p.setlabel(0x7030, "HPIBCMD(-0x14 [0x0c-0x20])")
	p.setlabel(0x72f1, "LED=Err(A)")
	p.setlabel(0x7394, "A=(X+A)")
	p.setlabel(0x73b8, "ERR=5")
	p.setlabel(0x77eb, "Err9_Calibrate_Error(A)")
	p.setlabel(0x7ad2, "DISP_LEV()")

	#----------------------------------------------------------------------
	# two Keyboard row (Page before Fig 8-25)

	p.setlabel(ea(p, 0x7045), "KEY_LocalRemote")
	p.setlabel(ea(p, 0x7047), "KEY_ManTrig")
	p.setlabel(ea(p, 0x704b), "KEY_DispLev")
	p.setlabel(ea(p, 0x704d), "KEY_ns")
	p.setlabel(ea(p, 0x704f), "KEY_us")
	p.setlabel(ea(p, 0x7051), "KEY_ms")
	p.setlabel(ea(p, 0x7053), "KEY_EVTS")
	p.setlabel(0x710e, "GET_KEY()")

	#----------------------------------------------------------------------
	# HP53xx EPROM structure
	hp53xx.eprom(p, 0x6000, 0x8000, 0x400)

	#----------------------------------------------------------------------
	#
	#hp53xx.nmi_debugger(p, p.m.w16(0x7ffc))

	hp53xx.chargen(p, chars=27)
	hp53xx.wr_test_val(p)

	#----------------------------------------------------------------------

	if True:
		for ax in range(0x703d,0x7055,2):
			x = const.w16(p, ax)
			x.a['EA'] = (ea(p, ax),)
			cpu.disass(p.m.w16(ax))
		for ax in range(0x707d,0x708f,2):
			x = const.w16(p, ax)
			eax = ea(p,ax)
			x.a['EA'] = (eax,)
			p.setlabel(eax, "SRVKEY_%04x" % ax)
			cpu.disass(p.m.w16(ax))

	p.setlabel(0x6912, "SRVKEY_DISP_012c")
	p.setlabel(0x6918, "SRVKEY_DISP_0124")
	p.setlabel(0x691e, "SRVKEY_DISP_0134")
	p.setlabel(0x6924, "SRVKEY_DISP_015c")
	p.setlabel(ea(p, 0x707d), "KEY_NOKEY")


	#----------------------------------------------------------------------

	hp5359_cmds = {
		"F":	"Frequency Mode",
		"P":	"Period Mode",
		"D":	"Delay",
		"W":	"Width",
		"SS":	"Step Size",
		"SU":	"Step Up",
		"SD":	"Step Down",
		"EN":	"Events Slope Negative",
		"EP":	"Events Slope Positive",
		"TP":	"External Trigger Positive Slope",
		"TN":	"External Trigger Negative Slope",
		"TM":	"Trigger Manual",
		"ID":	"Trigger Input Disable",
		"IE":	"Trigger Input Enable",
		"TF":	"Triggered Frequency On",
		"NF":	"Normal Frequency",
		"ON":	"Output Normal",
		"OC":	"Output Complement",
		"OA":	"Output Amplitude",
		"OO":	"Output Offset",
		"OL":	"Output Local",
		"SC":	"Single Cycle",
		"RA":	"Rearm",
		"NC":	"Normal Cycle",
		"OD":	"Output Disable",
		"OE":	"Output Enable",
		"SP":	"Sync Delay-Preset",
		"SA":	"Sync Delay-Auto",
		"C":	"Calibrate",
		"EC":	"External Compensation",
		"aE":	"External Compensation Enable",
		"aD":	"External Compensation Disable",
		"TE":	"Teach",
		"LN":	"Learn",
	}

	ncmd = 0x31
	ncmd0 = 0x14
	t0 = 0x6225
	t1 = 0x624d
	t2 = t1 + (ncmd-ncmd0) * 2

	for ax in range(t0,t1,2):
		const.txtlen(p, ax, 2)

	x = p.t.add(t0, t2, "tbl")
	x.blockcmt += "\n-\nHPIB CMD Table\n\n"
	p.setlabel(t0, "CMD_TABLE")

	x = p.t.add(t2, t2 + ncmd * 2, "tbl")
	x.blockcmt += "\n-\nHPIB command function Table\n\n"

	for ax in range(0, ncmd * 2, 2):
		const.txtlen(p, t0 + ax, 2)
		if p.m.rd(t0 + ax + 1) == 0:
			sx = p.m.ascii(t0 + ax, 1)
		else:
			sx = p.m.ascii(t0 + ax, 2)


		if sx in hp5359_cmds:
			ssx = " " + hp5359_cmds[sx]
		else:
			ssx = " ?"

		if ax < ncmd0 * 2:

			ay = 0x703d + ax + 0x0c * 2

		else:

			ay = t2 + ax - ncmd0 *2

		print(ax, sx, ssx, "%x" % ay)

		x = const.w16(p, ay)
		wx = p.m.w16(ay)
		x.a['EA'] = (ea(p, ay),)

		p.setlabel(ea(p, ay), "CMD_" + sx + ssx)
		cpu.disass(wx)

	# Overwrite this one
	p.setlabel(0x6a4e, "MAIN_LOOP()")

	#----------------------------------------------------------------------
	# SWI jmp's to X

	# @609d
	cpu.disass(0x6355)

	#----------------------------------------------------------------------
	#----------------------------------------------------------------------

	const.w16(p, 0x68b7)
	p.setlabel(0x68b7, "NUM_DIG")

	#----------------------------------------------------------------------

	const.byte(p, 0x7fa3, 7)
	const.byte(p, 0x7faa, 7)
	const.byte(p, 0x7fb1, 7)
	const.byte(p, 0x7fb8, 7)

	#----------------------------------------------------------------------

	def hp5359_nbr(p, adr):
		m = 0.0
		for ax in range(adr + 6, adr-1, -1):
			w = p.m.rd(ax)
			m *= .1
			m += w & 0xf
			m *= .1
			m += w >> 4
		e = p.m.s8(adr + 7)
		return "%.15fE%d" % (m,e)

	class dot_float(tree.tree):
		def __init__(self, p, adr):
			tree.tree.__init__(self, adr, adr + 8, "dot_float")
			p.t.add(self.start, self.end, self.tag, True, self)
			self.render = self.rfunc
			self.nbr = hp5359_nbr(p, adr)
			self.a['const'] = "FLOAT=" + self.nbr
			p.setlabel(adr, self.a['const'])

		def rfunc(self, p, t):
			s = ".FLOAT\t%s" % self.nbr
			return (s,)

	for i in range(0x7f03, 0x7fa3, 8):
		dot_float(p, i)

	#######################################################################
	while p.run():
		pass

	if True:

		def jmptbl(p, jmp, low, high, name, flow="call"):
			print("Call table for", name)
			x = p.t.find(jmp, "ins")
			l = []
			for i in range(low, high, 2):
				y = p.m.b16(i)
				l.append((flow, name, y))
			x.a['flow'] = l

		jmptbl(p, 0x6223, 0x6287, 0x62c1, "HPIBCMD", "cond")
		jmptbl(p, 0x703b, 0x703d, 0x708f, "KEYCMD")

		x = p.t.find(0x7422, "ins")
		x.a['flow'] = (("call", "SWI", 0x7018),)
		x = p.t.find(0x60a0, "ins")
		x.a['flow'] = (("call", "SWI", 0x6355),)


	p.hint(0x702e)['dot-page'] = "rankdir=LR"
	p.hint(0x6175)['dot-page'] = "rankdir=LR"
	p.hint(0x6442)['dot-page'] = "rankdir=LR"
	p.hint(0x6456)['dot-page'] = "rankdir=LR"
	p.hint(0x6486)['dot-page'] = "rankdir=LR"
	p.hint(0x64de)['dot-page'] = "rankdir=LR"
	p.hint(0x6b29)['dot-page'] = "rankdir=LR"
	p.hint(0x6da2)['dot-page'] = "rankdir=LR"
	p.hint(0x6dc3)['dot-page'] = "rankdir=LR"


	ff = topology.topology(p)
	p.g = ff
	ff.build_bb()
	ff.segment()
	ff.setlabels(p)
	ff.dump_dot()

	ff.xxx(p)

	#######################################################################

	for ax in (0x7307, 0x730b, 0x7b90, 0x7c94, 0x7c98):
		x = p.t.find(ax, "ins")
		hp53xx.sevenseg(p, x, p.m.rd(x.start + 1))

	#######################################################################

	import render
	r = render.render(p)

	r.render("/tmp/_hp5359a")
	#p.t.recurse()
	exit(0)

# Random notes:

# Power on TE:
# e2 e3 e4 e5 e6               ee               f6 f7 f8 f9 fa fb fc fd fe ff               107              10f              117              11f
# 3c 04 3e 01 00100000000000fb 00100000000000fa be b7 02 40 40 41 00 31 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000040000
# 3c 04 3e 01 00100000000000fb 00100000000000fa be 37 02 40 40 41 00 32 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000020000
# Period 10ms
# 3c 05 3e 01 00100000000000ff 00100000000000fa be 37 12 10 10 11 00 fd 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000010000
# Period 12.34ms
# 3c 05 3e 01 00123400000000ff 00100000000000fa be 37 12 10 10 11 00 fd 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000100000
# Width 4.567ms
# 3c 05 3e 01 00123400000000ff 00456700000000fe be 37 12 40 40 41 00 fd 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000400000
# Period 150ms
# 3c 05 3e 01 0015000000000000 00456700000000fe be 37 12 10 10 11 00 fd 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000200000
# Width 135ms
# 3c 05 3e 01 0015000000000000 0013500000000000 be 37 12 40 40 41 00 fd 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000400000
# Cal
# 3c 05 3e 01 0015000000000000 0013500000000000 be b7 02 40 40 41 00 32 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000800000
# Cal
# 3c 05 3e 01 0015000000000000 0013500000000000 be 37 02 40 40 41 00 32 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000400000
# Width 5ns
# 3c 05 3e 01 0015000000000000 00500000000000f8 be 37 12 40 40 41 00 f7 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 0000800000
# Display Levels
# 3c 05 3e 01 0015000000000000 00500000000000f8 be 37 02 40 00 09 00 f7 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 000010ff96
# Amp =1.00 Off=0.00
# 3c 05 3e 01 0015000000000000 00500000000000f8 be 37 02 40 00 09 00 f7 50 00100000000000f8 00100000000000f8 00100000000000f8 0010000000000004 000001de80

