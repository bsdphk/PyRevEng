#!/usr/local/bin/python
#
# This is a "real" task which disassembles the MC6800 ROM from a
# Hewlett Packard HP5370B Time Interval Counter.
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
import const
import tree
import pyreveng
import cpus.mc6800
import render
import topology

# Local classes
import hp53xx
import hp5370

#----------------------------------------------------------------------
# Set up the memory image

m = mem.byte_mem(0, 0x10000, 0, True, "big-endian")
# NB: the address bus is inverted, so we load from top down
m.fromfile("HP5370B.ROM", 0x7fff, -1)
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
hp53xx.eprom(p, cpu.disass, 0x6000, 0x8000, 0x400)
const.fill(p, hi=0x67ff)
const.fill(p, hi=0x6bff)
const.fill(p, hi=0x73ff)
const.fill(p, hi=0x77ff)
const.fill(p, hi=0x78ff)
const.fill(p, hi=0x7bff)

#######################################################################
#######################################################################
#######################################################################
#######################################################################
#
# Manual polishing below this point
#

p.t.blockcmt += """-
HP5370B ROM disassembly
=======================

"""

hp53xx.gpib_board(p)

p.t.blockcmt += """-
0x0050-0x005f	A16 Arming

	0x0050-0x0051:R	LDACSR signal
	0x0052-0x0053:R A16U21+A16U15 MUX
		0x0052:R A16 Service Switch
			0x80 = Loop
			0x10 = Read
			0x08 = Display
			0x04 = Write
			0x02 = ROM test
			0x01 = RAM test
	0x0054-0x0055:R	LEN2 signal
		0x0054:R
			0x80 = Oven heater ("LOVEN")
			0x40 = External Tb ("LEXT")
			0x3f = N/C
		0x0055:R
			0x80 = Event counter range/overflow flag ("HN30R")
			0x40 = End of measurement ("LPROC")
			0x20 = Sign of N0 ("SIGN")
			0x10 = Armed flag ("ERMD")
			0x08 = PLL out of lock
			0x04 = N0 range/overflow flag
			0x03 = 257*(N1-N2) counter bits
	0x0056-0x0057:R	LEN1 signal
		N0 counter, see TB1 description
	0x0058-0x0059:R	LEN0 signal
		257*(N1-N2) counter, see TB1 description
	0x005a-0x005b:R	A16U17+A16U19 MUX
		 Eventcounter
	{more}
"""

hp53xx.display_board(p)

p.t.blockcmt += """-
0x0080-0x0200	RAM

	0x0080-0x0086:	SW \  FLOAT
	0x0087-0x008d:	SZ  | stack
	0x008e-0x0094:	SY  > SW=top
	0x0095-0x009b:	SX  | SX=bot
	0x009c-0x00a2:	SA /  SA=spill

	0x00ae:	0b.......0: EA0 Ext Arm dis
	       	0b.......1: EA1 Ext Arm ena
	0x00b6:
		0b.....000: FN3 Freq
		0b.....001: FN4 Period
		0b.....010: FN1 TI
		0b.....100: FN2 TrigLevel
		0b.....101: FN5 ???
		0b..00....: MD1 FP rate
		0b..01....: MD2 Hold until MR
		0b..10....: MD3 Fast
		0b..11....: MD4 Fast+SRQ

	0x00b7:
		0b....X...: SE[12]
		0b......X.: SA[12]
		0b.......X: SO[12]
	0x00bb:
		0b......XX: FP/TI Overflow bits
	0x00bc:
		0b...XX...: IN[14]
	0x00c0-0x00c6:	REF_VALUE (FLOAT)
	0x00f2-0x00f3:	Freq/Period
	0x00f4-0x00f5:	TI
		0b0....... ........ Ascii Output (TB0)
		0b1....... ........ Binary Output (TB1)
	0x00f6-0x00f7:	Triglev/FN5
		0b........ ....0000 SS1 1 sample
		0b........ ....0001 SS2 100 sample
		0b........ ....0010 SS3 1k sample
		0b........ ....0011 SS4 10k sample
		0b........ ....0100 SS5 100k sample
		0b........ ....0101 GT2 0.01s
		0b........ ....0110 GT3 0.1s
		0b........ ....0111 GT4 1s
		0b........ .000.... ST1 Mean
		0b........ .001.... ST2 Stddev
		0b........ .010.... ST3 Min
		0b........ .011.... ST4 Max
		0b........ .100.... ST5 Disp Ref
		0b........ .101.... ST7 Disp Evt
		0b........ .111.... ST9 Disp All
		0b........ 0....... Ref clear
		0b........ 1....... Ref set

	0x0116-0x011c:	MAX_VALUE (FLOAT)
	0x011d-0x0123:	MIN_VALUE (FLOAT)
	0x0124-0x012a:
	0x012b-0x0131:
	0x0132-0x0138:	#Events ? (FLOAT?)
	0x0139-0x013f:

	0x0140-0x014f:	Led buffer
		0bX.......: DP
		0b....XXXX: BCD

	0x016c-0x016d: GPIB transmit-pointer
	0x016f-0x0182: GPIB output buffer
		"...,...,...,.E+##\r\n"

0x4000-?	Possibly Service/Expansion EPROM
0x6000-0x7fff	EPROMS

"""


class dot_24bit(tree.tree):
	def __init__(self, p, adr, len = 1, fmt = "0x%06x"):
		tree.tree.__init__(self, adr, adr + len * 3, "dot-24bit")
		p.t.add(self.start, self.end, self.tag, True, self)
		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t):
		s = ".24bit\t"
		d = ""
		for i in range(t.start, t.end, 3):
			x = p.m.b32(i) >> 8
			s += d
			s += self.fmt % x
			d += ", "
		return (s,)


#######################################################################
# 0x6f00...0x7000 = x^2/256 table

#######################################################################
# Floating point constants
# likely related to converting to SI units
#
x = hp5370.float(p, 0x614c)
x.lcmt("= 2^31 * 5*10^-9 * 10^-6 (%.9e)\n" % (math.ldexp(1,31)*5e-9*1e-6))

x = hp5370.float(p, 0x619c)
x.lcmt("= 2^23 * 5*10^-9 * 10^-9 (%.9e)\n" % (math.ldexp(1,23)*5e-9*1e-9))

x = hp5370.float(p, 0x61a3)
x.lcmt("= 2^31 * 5*10^-9 (%.9e)\n" % (math.ldexp(1,31)*5e-9))

x = hp5370.float(p, 0x69dd)
x.lcmt("= 2^23 * 5*10^-9 * 10^-9 (%.9e)\n" % (math.ldexp(1,23)*5e-9*1e-9))

x = hp5370.float(p, 0x69e4)
x.lcmt("= 2^31 * 5*10^-9 (%.9e)\n" % (math.ldexp(1,31)*5e-9))

#######################################################################
const.byte(p, 0x7a75, 15)
const.byte(p, 0x7a84, 8)
const.byte(p, 0x7a8c, 8)
const.byte(p, 0x7a95, 7)
const.byte(p, 0x77f7, 7)

#######################################################################
x = p.t.add(0x6b09,0x6b23, "tbl")
x.blockcmt += "Table Keyboard or LED related ?\n"
const.byte(p, 0x6b09, 8)
const.byte(p, 0x6b11, 8)
const.byte(p, 0x6b19, 8)
const.byte(p, 0x6b21, 2)

#######################################################################
x = p.t.add(0x6b23,0x6b32, "tbl")
x.blockcmt += "Table of NSAMP = {1,100,1k,10k,100k}\n"
dot_24bit(p, 0x6b23, 1, "%d")
dot_24bit(p, 0x6b26, 1, "%d")
dot_24bit(p, 0x6b29, 1, "%d")
dot_24bit(p, 0x6b2c, 1, "%d")
dot_24bit(p, 0x6b2f, 1, "%d")

#######################################################################
x = p.t.add(0x6b32,0x6b3b, "tbl")
x.blockcmt += "Table sqrt(1k,10k,100k)\n"
dot_24bit(p, 0x6b32, 1, "%d")
dot_24bit(p, 0x6b35, 1, "%d")
dot_24bit(p, 0x6b38, 1, "%d")

#######################################################################

# strings
const.txtlen(p,0x78f3,4)
const.txtlen(p,0x78f7,6)
const.txtlen(p,0x78fd,2)

p.setlabel(0x77d7, "OUT_STRINGS")
for i in range(0x77d7,0x77f7,4):
	const.txtlen(p,i,4)

const.ptr(p, 0x7915, 2)

#######################################################################
# BCD->7seg table

hp5370.chargen(p, 0x7e30)
hp5370.hpib_cmd_table(p, 0x7c64)
hp5370.keyboard_dispatch(p, cpu)
hp5370.hpib_arg_range(p, 0x7d6c)
hp5370.hpib_tbl_idx(p, 0x7d88)
hp5370.dispatch_table_arg(p, 0x7d66, cpu)
hp5370.dispatch_table_noarg(p, 0x7d30, cpu)
hp5370.dsp_dispatch(p, cpu)
hp5370.square_table(p)
hp53xx.wr_test_val(p)

if True:
	###########################################################
	const.ptr(p, 0x7909, 2)
	y = p.m.b16(0x7909)
	cpu.disass(y)
	p.setlabel(y, "HPIB_CMD_PARSE")
	ins = cpu.disass(0x7c62)
	ins.flow("cond", "XXX", y)

#######################################################################
while p.run():
	pass

#######################################################################
hp53xx.nmi_debugger(p, cpu)

#######################################################################
# Manual markup

if True:
	x = p.t.add(0x7d96, 0x7da3, "block")
	x.blockcmt += "RESET entry point\n"
	x = p.t.add(0x7da3, 0x7db1, "block")
	x.blockcmt += "Self & Service test start\n"
	x = p.t.add(0x7db1, 0x7de8, "block")
	x.blockcmt += "RAM test\n"
	x = p.t.add(0x7de8, 0x7df8, "block")
	x.blockcmt += 'Display "Err 6.N" RAM error\n'
	x = p.t.add(0x7df8, 0x7e30, "block")
	x.blockcmt += 'Display "Err N.M\n'
	x = p.t.add(0x7e40, 0x7ebf, "block")
	x.blockcmt += "EPROM test\n"
	x = p.t.add(0x7ebf, 0x7ef9, "block")
	x.blockcmt += 'A16 Service Switch bit 2: "Write Test"\n'
	x = p.t.add(0x7ef9, 0x7f24, "block")
	x.blockcmt += 'A16 Service Switch bit 3: "Display Test"\n'
	x = p.t.add(0x7f24, 0x7f46, "block")
	x.blockcmt += 'A16 Service Switch bit 4: "Read Test"\n'
	x = p.t.add(0x7f46, 0x7f4d, "block")
	x.blockcmt += 'A16 Service Switch bit 7: "Loop Tests"\n'
	x = p.t.add(0x7f6b, 0x7f79, "block")
	x.blockcmt += "LAMP/LED test\n"

#######################################################################
if True:
	p.setlabel(0x0052, "A16.ServSwich")
	aa = 0x80
	for ii in ("SW", "SZ", "SY", "SX", "SA"):
		for jj in ('m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'e'):
			p.setlabel(aa, ii + "." + jj)
			aa += 1

	p.setlabel(0x00c0, "REF_VALUE")
	p.setlabel(0x0116, "MAX_VALUE")
	p.setlabel(0x011d, "MIN_VALUE")

	p.setlabel(0x6015, "HPIB_SEND_TRIG_LVL(X)")
	p.setlabel(0x6048, "LED=0.00")
	p.setlabel(0x6054, "CMD(X+A)")
	p.setlabel(0x6057, "X=PARAM(CUR)")
	p.setlabel(0x6064, "Delay(X)")
	p.setlabel(0x608d, "LED_BLANK()")
	p.setlabel(0x608f, "LED_FILL(A)")
	p.setlabel(0x612a, "*=10.0()")
	p.setlabel(0x6145, "CLK_TO_TIME()")
	p.setlabel(0x6153, "SHOW_RESULT()")
	p.setlabel(0x61f8, "GPIB_RX_ONE()")
	p.setlabel(0x620b, "TIMEBASE_TO_HPIB()")
	p.setlabel(0x6217, "CHK_PLL_LOCK()")
	p.setlabel(0x623e, "ERR4_PLL_UNLOCK")
	p.setlabel(0x6244, "LedFillMinus()")
	p.setlabel(0x624d, "ERR2_TI_OVERRANGE")
	p.setlabel(0x62cf, "LED=LEDBUF()")
	p.setlabel(0x6344, "X+=A()")
	p.setlabel(0x63df, "ERR3_UNDEF_ROUTINE")
	p.setlabel(0x66ea, "ERR5_UNDEF_KEY")
	p.setlabel(0x6918, "REF_ADJ()")
	p.setlabel(0x69f5, "REF_VALUE=AVG()")
	p.setlabel(0x6a0c, "REF_VALUE=0.0()")
	p.setlabel(0x700c, "DUP()")
	p.setlabel(0x700f, "DROP()")
	p.setlabel(0x7015, "ROLL()")
	p.setlabel(0x7018, "ADD()")
	p.setlabel(0x701b, "SUB()")
	p.setlabel(0x701e, "MULTIPLY()")
	p.setlabel(0x7021, "DIVIDE()")
	p.setlabel(0x7048, "PUSH(?*X)")
	p.setlabel(0x705c, "*X=SX")
	p.setlabel(0x7069, "memcpy(*0xae,*0xac,7)")
	p.setlabel(0x707d, "Swap(SX,SY)")
	p.setlabel(0x70ef, "SY.m+=SX.m()")
	p.setlabel(0x7115, "A=OR(SX.m)")
	p.setlabel(0x7122, "A=OR(SY.m)")
	p.setlabel(0x714b, "SY.m-=SX.m()")
	p.setlabel(0x7277, "SY==SX?()")
	p.setlabel(0x72d3, "NEGATE()")
	p.setlabel(0x72ee, "SX=0.0()")
	p.setlabel(0x72fb, "NORMRIGHT(*X,A)")
	p.setlabel(0x7310, "NORMLEFT(*X,A)")
	p.setlabel(0x7326, "NORM(SX,SY)")
	p.setlabel(0x7356, "SY=0.0()")
	p.setlabel(0x7363, "NORM(SY)")
	p.setlabel(0x73c3, "SET_OFLOW()")
	p.setlabel(0x73ca, "LED_ERR(A)")
	p.setlabel(0x7403, "RESULT_TO_GPIB()")
	p.setlabel(0x740b, "FLOAT_FMT()")
	p.setlabel(0x76e6, "ERR1_UNDEF_CMDa")
	p.setlabel(0x7716, "LED_TO_GPIB()")
	p.setlabel(0x798c, "UPDATE_LAMPS()")
	p.setlabel(0x790c, "LAMP_TEST()")
	p.setlabel(0x790f, "HPIB_RECV(*X,A)")
	p.setlabel(0x7912, "HPIB_SEND(*X,A)")
	p.setlabel(0x7918, "FAST_BINARY()")
	p.setlabel(0x7936, "KEY_PRELL")
	p.setlabel(0x7987, "GET_FN()")
	p.setlabel(0x7a69, "*X=NIBBLES(A)")
	p.setlabel(0x7b38, "EXIT_FAST_BINARY")
	p.setlabel(0x7bc6, "RESET_STACK_MAIN")
	p.setlabel(0x7cb2, "SP?")
	p.setlabel(0x7cb8, "COMMA?")
	p.setlabel(0x7cbc, "CR?")
	p.setlabel(0x7cc0, "NL?")
	p.setlabel(0x7ccb, "TOLOWER")
	p.setlabel(0x7ccd, "BELOW_A?")
	p.setlabel(0x7cd1, "ABOVE_Z?")
	p.setlabel(0x7d19, "ERR1_UNDEF_CMDb")
	p.setlabel(0x7d21, "CMD_FOUND")
	p.setlabel(0x7d3f, "BELOW_0")
	p.setlabel(0x7d43, "ABOVE_9")
	p.setlabel(0x7de8, "ERR6.N")
	p.setlabel(0x7df8, "ERRN.M")
	p.setlabel(0x7e40, "ROMTEST")
	p.setlabel(0x7ec5, "WR_TEST")
	p.setlabel(0x7eff, "DISPLAYTEST")
	p.setlabel(0x7f24, "RD_TEST")
	p.setlabel(0x7f4a, "TEST_LOOP")

#######################################################################

for ax in (0x7e23, 0x7e27):
	ins = cpu.ins[ax]
	const.seven_seg_lcmt(ins, p.m.rd(ins.lo + 1))

#######################################################################
# Move instructions to tree

cpu.to_tree()

#######################################################################

p.g = topology.topology(p)
p.g.build_bb()

if True:
	p.g.add_flow("IRQ", p.m.b16(0x7ff8))
	p.g.add_flow("SWI", p.m.b16(0x7ffa))
	p.g.add_flow("NMI", p.m.b16(0x7ffc))
	p.g.add_flow("RST", p.m.b16(0x7ffe))

if True:
	p.g.segment()
	p.g.setlabels(p)

	p.g.dump_dot()

	p.g.xxx(p)

r = render.render(p)
r.add_flows()
r.render("/tmp/_.hp5370b.txt")
