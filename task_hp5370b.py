#!/usr/local/bin/python
#

from __future__ import print_function

import math

import mem
import array

import tree
import pyreveng

import cpu_mc6800

headcmt = """
HP5370B ROM disassembly
=======================

Address Map:
------------

0x0000-0x0003	GPIB {P8-30}

	0x0000:R Data In
	0x0000:W Data Out
	0x0001:R Inq In
	0x0001:W Status Out
	0x0002:R Cmd In
	0x0002:W Control Out
		0x10 = EOI out {0x61e9}
	0x0003:R State In

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
	0x0056-0x0057:R	LEN1 signal
	0x0058-0x0059:R	LEN0 signal
	0x005a-0x005b:R	A16U17+A16U19 MUX
		 Eventcounter
	{more}

0x0060-0x007f	Front panel

	0x0060:R Buttons
		0xf0: scan lines
		0x07: sense lines
	0x0060-0x006f:W	LEDS
	0x0070-0x007f:W	7segs

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
	0x00bc:
		0b...XX...: IN[14]
	0x00c0-0x00c6:	REF_VALUE (FLOAT)
	0x00f2-0x00f3:	Freq/Period
	0x00f4-0x00f5:	TI
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
		0b........ .111.... ST3 Disp All
		0b........ 0....... Ref clear
		0b........ 1....... Ref set
		
	0x00f4:
		0bX.......: TB[01]

	0x0116-0x011c:	MAX_VALUE (FLOAT)
	0x011d-0x0123:	MIN_VALUE (FLOAT)
	0x0124-0x012a:
	0x012b-0x0131:
	0x0132-0x0138:	#Events ? (FLOAT?)

	0x0140-0x014f:	Led buffer
		0bX.......: DP
		0b....XXXX: BCD

	0x016c-0x016d: GPIB transmit-pointer
	0x016f-0x0182: GPIB output buffer
		"...,...,...,.E+##\r\n"

0x4000-?	Possibly Service/Expansion EPROM
0x6000-0x7fff	EPROMS
				
"""


# Explanation of the HP5370B HPIB Commands
gpib_expl = {
	"FN1":	"Time Interval",
	"FN2":	"Trigger Levels",
	"FN3":	"Frequency",
	"FN4":	"Period",
	"FN5":	"???",
	"GT1":	"Single Period",
	"GT2":	"0.01s",
	"GT3":	"0.1s",
	"GT4":	"1s",
	"ST1":	"Mean",
	"ST2":	"StdDev",
	"ST3":	"Min",
	"ST4":	"Max",
	"ST5":	"Disp Ref",
	"ST6":	"Clr Ref",
	"ST7":	"Disp Evts",
	"ST8":	"Set Ref",
	"ST9":	"Disp All",
	"SS1":	"Sample Size = 1",
	"SS2":	"Sample Size = 100",
	"SS3":	"Sample Size = 1k",
	"SS4":	"Sample Size = 10k",
	"SS5":	"Sample Size = 100k",
	"MD1":	"FP Rate",
	"MD2":	"Hold until MR",
	"MD3":	"Fast",
	"MD4":	"Fast + SRQ",
	"IN1":	"Input: Start+Stop",
	"IN2":	"Input: Stop+Stop",
	"IN3":	"Input: Start+Start",
	"IN4":	"Input: Stop+Start",
	"SA1":	"Start Pos",
	"SA2":	"Start Neg",
	"SO1":	"Stop Pos",
	"SO2":	"Stop Neg",
	"SE1":	"Arm Pos",
	"SE2":	"Arm Neg",
	"AR1":	"+T.I. Arming Only",
	"AR2":	"+T.I. Arming",
	"EH0":	"Ext Holdoff dis",
	"EH1":	"Ext Holdoff ena",
	"EA0":	"Ext Arm dis",
	"EA1":	"Ext Arm ena",
	"IA1":	"Internal Arm Auto",
	"IA2":	"Start Chan Arm",
	"IA3":	"Stop Chan Arm",
	"MR":	"Manual Rate",
	"MI":	"Manual Input",
	"SL":	"Slope Local",
	"SR":	"Slope Remote",
	"TL":	"Trigger Local",
	"TR":	"Trigger Remote",
	"TE":	"Teach",
	"PC":	"Period Complement",
	"TB0":	"Ascii",
	"TB1":	"Binary",
	"SB":	"Sample Size Binary",
	"LN":	"Learn",
	"TA":	"Trigger Start",
	"TO":	"Trigger Stop",
}

#######################################################################
# HP5370B uses its own (weird|smart) floating point format.
#
# As far as I can tell, it looks like this: S{1}M{47}E{8} where the
# exponent is 2's complement.  But there are two scaling factors 
# involved, so the value is:  (S * M{31.16} * 2^e * 5e-9)
#
# XXX: Hmm, the mantissa may be a 32.16 2' complement number...
#

def float_render(p, a):
	x = p.m.rd(a + 0)
	if x & 0x80:
		s = -1
		x ^= 0x80
	else:
		s = 1
	m =  math.ldexp(x, 24)
	m += math.ldexp(p.m.rd(a + 1), 16)
	m += math.ldexp(p.m.rd(a + 2), 8)
	m += math.ldexp(p.m.rd(a + 3), 0)
	m += math.ldexp(p.m.rd(a + 4), -8)
	m += math.ldexp(p.m.rd(a + 5), -16)
	e =  p.m.s8(a + 6)
	v = math.ldexp(m * 5e-9, e)
	x = "%.9e" % v
	if x.find(".") == -1 and x.find("e") == -1:
		x = x + "."
	print("FLOAT", "%x" % a, x)
	return x

class dot_byte(tree.tree):
	def __init__(self, p, adr, len = 1, fmt="0x%02x"):
		tree.tree.__init__(self, adr, adr + len, "dot-byte")
		p.t.add(self.start, self.end, self.tag, True, self)
		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".BYTE\t"
		d = ""
		for i in range(t.start, t.end):
			x = p.m.rd(i)
			s += d
			s += self.fmt % x
			d = ", "
		return (s,)

class dot_word(tree.tree):
	def __init__(self, p, adr, len = 1, fmt = "0x%04x"):
		tree.tree.__init__(self, adr, adr + len * 2, "dot-word")
		p.t.add(self.start, self.end, self.tag, True, self)
		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".WORD\t"
		d = ""
		for i in range(t.start, t.end, 2):
			x = p.m.b16(i)
			s += d
			s += self.fmt % x
			d += ", "
		return (s,)

class dot_24bit(tree.tree):
	def __init__(self, p, adr, len = 1, fmt = "0x%06x"):
		tree.tree.__init__(self, adr, adr + len * 3, "dot-24bit")
		p.t.add(self.start, self.end, self.tag, True, self)
		self.render = self.rfunc
		self.fmt = fmt

	def rfunc(self, p, t, lvl):
		s = ".24bit\t"
		d = ""
		for i in range(t.start, t.end, 3):
			x = p.m.b32(i) >> 8
			s += d
			s += self.fmt % x
			d += ", "
		return (s,)

class dot_ascii(tree.tree):
	def __init__(self, p, adr, len):
		tree.tree.__init__(self, adr, adr + len, "dot-ascii")
		p.t.add(adr, adr + 1, "dot-ascii", True, self)
		self.render = self.rfunc
		self.txt = p.m.ascii(adr, len)
		p.setlabel(adr, "TXT='" + self.txt + "'")

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'" + self.txt + "'"
		return (s,)

class dot_code(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 2, "dot-code")
		p.t.add(adr, adr + 2, "dot-code", True, self)
		self.render = self.rfunc
		t = p.m.b16(adr)
		# p.markbb(t, ".code")
		p.todo(t, p.cpu.disass)
		self.a['EA'] = (t,)

	def rfunc(self, p, t, lvl):
		s = ".CODE\t%04x" % p.m.b16(t.start)
		return (s,)

class dot_ptr(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 2, "dot-ptr")
		p.t.add(adr, adr + 2, "dot-ptr", True, self)
		self.render = self.rfunc
		t = p.m.b16(adr)
		self.a['EA'] = (t,)

	def rfunc(self, p, t, lvl):
		s = ".PTR\t%04x" % p.m.b16(t.start)
		return (s,)

class dot_float(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 7, "dot_float")
		p.t.add(adr, adr + 7, "dot-float", True, self)
		self.render = self.rfunc
		self.nbr = float_render(p, adr)
		p.setlabel(adr, "FP=" + self.nbr)

	def rfunc(self, p, t, lvl):
		s = ".FLOAT\t%s" % self.nbr
		return (s,)

#######################################################################
# And there they go...

dn="/rdonly/Doc/TestAndMeasurement/HP5370B/Firmware/"

m = mem.byte_mem(0, 0x10000, 0, True)
m.bcols = 3
p = pyreveng.pyreveng(m)
p.cmt_start = 48
p.cpu = cpu_mc6800.mc6800()

# The HP5370B inverts the address bus, so start at the end and count down:
p.m.fromfile(dn + "HP5370B.ROM", 0x7fff, -1)

p.t.blockcmt += headcmt

#######################################################################
# The image was orginally written for 8 1K*8 (2708 ?) EPROMS
# This structure still shows, with individual checksums and
# chip numbers in each 1KB of the image.


def do_eprom(p,start,eprom_size):
	x = p.t.add(i, i + eprom_size, "eprom")
	x.blockcmt += "EPROM at 0x%x-0x%x\n" % (i, i + eprom_size - 1)

	# Calculate checksum
	j = ~p.m.b16(i) 
	for jj in range(2, eprom_size):
		j += p.m.rd(i + jj)
	j &= 0xffff
	if j == 0xffff:
		j = "OK"
	else:
		j = "BAD"

	x = dot_word(p, i)
	x.cmt.append("EPROM checksum (%s)" % j)

	x = dot_byte(p, i + 2)
	x.cmt.append("EPROM number")

	# Handle any 0xff fill at the end of this EPROM
	n = 0
	for a in range(i + eprom_size - 1, i, -1):
		if p.m.rd(a) != 0xff:
			break;
		n += 1
	if n > 1:
		x = p.t.add(i + eprom_size - n, i + eprom_size, "fill")
		x.render = ".FILL\t%d, 0xff" % n

for i in range(0x6000,0x8000,0x400):
	do_eprom(p, i, 0x400)

#######################################################################
# NMI/GPIB debugger

xnmi = p.t.add(0x7f79, 0x7ff8, "src")
xnmi.blockcmt += """
NMI based GPIB debugger interface.
"""

#######################################################################
# 0x6f00...0x7000 = x^2/256 table

#######################################################################
# Floating point constants
# likely related to converting to SI units
#
x = dot_float(p, 0x614c)
x.cmt.append("= 2^31 * 5*10^-9 * 10^-6 (%.9e)\n" % (math.ldexp(1,31)*5e-9*1e-6))

x = dot_float(p, 0x619c)
x.cmt.append("= 2^23 * 5*10^-9 * 10^-9 (%.9e)\n" % (math.ldexp(1,23)*5e-9*1e-9))

x = dot_float(p, 0x61a3)
x.cmt.append("= 2^31 * 5*10^-9 (%.9e)\n" % (math.ldexp(1,31)*5e-9))

x = dot_float(p, 0x69dd)
x.cmt.append("= 2^23 * 5*10^-9 * 10^-9 (%.9e)\n" % (math.ldexp(1,23)*5e-9*1e-9))

x = dot_float(p, 0x69e4)
x.cmt.append("= 2^31 * 5*10^-9 (%.9e)\n" % (math.ldexp(1,31)*5e-9))

#######################################################################
dot_byte(p, 0x7a75, 15)
dot_byte(p, 0x7a84, 8)
dot_byte(p, 0x7a8c, 8)
dot_byte(p, 0x7a95, 7)
dot_byte(p, 0x77f7, 7)

#######################################################################
x = p.t.add(0x6b09,0x6b23, "tbl")
x.blockcmt += "Table Keyboard or LED related ?\n"
dot_byte(p, 0x6b09, 8)
dot_byte(p, 0x6b11, 8)
dot_byte(p, 0x6b19, 8)
dot_byte(p, 0x6b21, 2)

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
x = p.t.add(0x6f00,0x7000, "tbl")
x.blockcmt += "Table of I^2>>8\n"

#######################################################################
# Table of EPROM ranges
x = p.t.add(0x7ead, 0x7ebf, "tbl")
x.blockcmt += "Table of EPROM start addresses\n"
for a in range(0x7ead, 0x7ebf, 2):
	dot_ptr(p, a)

#######################################################################
x = p.t.add(0x7eed, 0x7ef9, "tbl")
x.blockcmt += "Write test byte values (?)\n"
for i in range(x.start, x.end):
	dot_byte(p, i)

#######################################################################
# CPU vectors

def vec(p,a,n):
	x = dot_code(p, a)
	x.blockcmt += n + " VECTOR\n"
	w = p.m.b16(a)
	p.setlabel(w, n + "_ENTRY")
	p.markbb(w, ("call", n, None))

vec(p,0x7ffe,"RST")
vec(p,0x7ffc,"NMI")
vec(p,0x7ffa,"SWI")
vec(p,0x7ff8,"IRQ")

p.t.add(0x7ff8, 0x8000, "tbl").blockcmt += """
CPU Vector Table
"""

#######################################################################
# jmp table 
dspf= ("AVG", "STD", "MIN", "MAX", "REF", "EVT", "DS6", "DS7")
j=0
for i in range(0x6848,0x6858,2):
	x = dot_code(p, i)
	w = p.m.b16(i)
	p.setlabel(w, "DSP_" + dspf[j])
	j += 1

x=p.t.add(0x6848,0x6858,"tbl")
x.blockcmt += "Table of display functions\n"
p.setlabel(0x6848, "DSP_FUNC_TABLE")
#######################################################################

# strings
dot_ascii(p,0x78f3,4)
dot_ascii(p,0x78f7,6)
dot_ascii(p,0x78fd,2)
for i in range(0x77d7,0x77f7,4):
	dot_ascii(p,i,4)

dot_code(p, 0x7909)
dot_ptr(p, 0x7915)
#######################################################################
# BCD->7seg table
x = p.t.add(0x7e30, 0x7e40, "7seg")
x.blockcmt += "BCD to 7 segment table\n"
sevenseg = "0123456789.#-Er "
for i in range(0,16):
	y = dot_byte(p, x.start + i)
	y.cmt.append("'%s'" % sevenseg[i])

#######################################################################
# List of two-letter HPIB commands
#
hpib_cmd = list()
x = p.t.add(0x7c64, 0x7c98, "cmd-table")
x.blockcmt += "Table of two-letter HPIB commands\n"
for i in range(0x7c64,0x7c98,2):
	dot_ascii(p,i,2)
	hpib_cmd.append(p.m.ascii(i, 2))
	
#######################################################################
# jmp table, see 7962->6054->63ec

dot_ptr(p, 0x6403)
ba = p.m.b16(0x6403)
ea = p.m.b16(0x6405)

aa = ba
for col in range(8,0,-1):
	p.setlabel(aa, "Keyboard_Column_%d" % col)
	for row in range(1,5):
		x = dot_code(p, aa)
		aa += 2

x = p.t.add(ba, ea, "tbl")
x.blockcmt += """
Dispatch table for Keyboard commands
"""

p.setlabel(0x66a1, "KEY_Ext_Arm")
p.setlabel(0x6669, "KEY_Ext_Hold_Off")
p.setlabel(0x6613, "KEY_RESET")

#######################################################################
# Table of HPIB numeric arg ranges
# & pointer into command dispatch table
#
hpib_numcmds = 14

dot_ptr(p, 0x6405)
ba = p.m.b16(0x6405)
ea = p.m.b16(0x6407)

b = 0x7d6c
e = b + 2 * hpib_numcmds
x = p.t.add(b, e, "arg-table")
x.blockcmt += "Table of legal range of numeric argument for HPIB cmd\n"

t = 0x7d88
x = p.t.add(t, t + hpib_numcmds, "idx-table")
x.blockcmt += "Index into cmd table, add numeric arg\n"

for i in range(0, hpib_numcmds):
	x = dot_byte(p, b + 2 * i, 2)
	lo = p.m.rd(b + 2 * i)
	hi = p.m.rd(b + 2 * i + 1)
	x.cmt.append(hpib_cmd[i])

	x = dot_byte(p, t + i)
	x.cmt.append(hpib_cmd[i] + "[%d-%d]" % (lo, hi))
	pp = ba + p.m.rd(t + i) * 2
	for xx in range(lo, hi + 1):
		x = dot_code(p, pp + (xx - lo) * 2)
		tt = "%s%d" % (hpib_cmd[i], xx)
		x.cmt.append("%s %s" % (tt, gpib_expl[tt]))
		w = p.m.b16(x.start)
		p.setlabel(w, "CMD_" + tt + "_" + gpib_expl[tt])

x = p.t.add(ba, ea, "tbl")
x.blockcmt += """
Dispatch table for GPIB commands with numeric argument
"""

#######################################################################
# Table of GPIB commands without numeric args
# XXX: should find these automatically, but the indir an the jumps are
# XXX: not found yet...

p.setlabel(0x61aa,"CMD_LN_Learn")
p.setlabel(0x61ca,"CMD_TE_Teach")
p.setlabel(0x7968,"CMD_MR_ManualRate")

dot_ptr(p, 0x6407)
ba = p.m.b16(0x6407)
n = 0
for j in range(hpib_numcmds, len(hpib_cmd)):
	aa = ba + n * 2
	n += 1
	x = dot_code(p, aa)
	w = p.m.b16(x.start)
	tt = hpib_cmd[j]
	x.cmt.append("%s %s" % (tt, gpib_expl[tt]))
	p.setlabel(w, "CMD_" + tt + "_" + gpib_expl[tt])

x = p.t.add(ba, aa + 2, "tbl")
x.blockcmt += """
Dispatch table for GPIB commands without argument
"""

#######################################################################
while p.run():
	#study(p)
	pass
#######################################################################
# Manual markup

x = p.t.add(0x7d96, 0x7da3, "block")
x.blockcmt += """
RESET entry point
"""
x = p.t.add(0x7da3, 0x7db1, "block")
x.blockcmt += """
Self & Service test start
"""
x = p.t.add(0x7db1, 0x7de8, "block")
x.blockcmt += """
RAM test
"""
x = p.t.add(0x7de8, 0x7df8, "block")
x.blockcmt += """
Display "Err 6.N" RAM error
"""

x = p.t.add(0x7df8, 0x7e30, "block")
x.blockcmt += """
Display "Err N.M" 
"""

x = p.t.add(0x7e40, 0x7ebf, "block")
x.blockcmt += """
EPROM test
"""
x = p.t.add(0x7ebf, 0x7ef9, "block")
x.blockcmt += """
A16 Service Switch bit 2: "Write Test"
"""
x = p.t.add(0x7ef9, 0x7f24, "block")
x.blockcmt += """
A16 Service Switch bit 3: "Display Test"
"""
x = p.t.add(0x7f24, 0x7f46, "block")
x.blockcmt += """
A16 Service Switch bit 4: "Read Test"
"""
x = p.t.add(0x7f46, 0x7f4d, "block")
x.blockcmt += """
A16 Service Switch bit 7: "Loop Tests"
"""
x = p.t.add(0x7f6b, 0x7f79, "block")
x.blockcmt += """
LAMP/LED test
"""

#######################################################################
p.setlabel(0x0052, "A16.ServSwich")
aa = 0x80
for ii in ("SW", "SZ", "SY", "SX", "SA"):
	for jj in ('m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'e'):
		p.setlabel(aa, ii + "." + jj)
		aa += 1

p.setlabel(0x00c0, "REF_VALUE")
p.setlabel(0x0116, "MAX_VALUE")
p.setlabel(0x011d, "MIN_VALUE")

p.setlabel(0x6057, "X=PARAM(CUR)")
p.setlabel(0x6064, "Delay(X)")
p.setlabel(0x608d, "LED_BLANK()")
p.setlabel(0x608f, "LED_FILL(A)")
p.setlabel(0x612a, "*=10.0()")
p.setlabel(0x6153, "SHOW_RESULT()")
p.setlabel(0x623e, "ERR4_PLL_UNLOCK")
p.setlabel(0x6244, "LedFillMinus()")
p.setlabel(0x624d, "ERR2_TI_OVERRANGE")
p.setlabel(0x62cf, "LED=LEDBUF()")
p.setlabel(0x6344, "X+=A()")
p.setlabel(0x6376, "LED=0.00")
p.setlabel(0x63df, "ERR3_UNDEF_ROUTINE")
p.setlabel(0x66ea, "ERR5_UNDEF_KEY")
p.setlabel(0x69f5, "REF_VALUE=AVG()")
p.setlabel(0x6a0c, "REF_VALUE=0.0()")
p.setlabel(0x7048, "PUSH(?*X)")
p.setlabel(0x705c, "*X=SX")
p.setlabel(0x7069, "memcpy(*0xae,*0xac,7)")
p.setlabel(0x707d, "Swap(SX,SY)")
p.setlabel(0x708c, "DUP()")
p.setlabel(0x70ab, "DROP()")
p.setlabel(0x70d2, "ADD()")
p.setlabel(0x70ef, "SY.m+=SX.m()")
p.setlabel(0x7115, "A=OR(SX.m)")
p.setlabel(0x7122, "A=OR(SY.m)")
p.setlabel(0x712f, "SUB()")
p.setlabel(0x714b, "SY.m-=SX.m()")
p.setlabel(0x7173, "MULTIPLY()")
p.setlabel(0x71fa, "DIVIDE()")
p.setlabel(0x72d3, "NEGATE()")
p.setlabel(0x72ee, "SX=0.0()")
p.setlabel(0x72fb, "NORMRIGHT(*X,A)")
p.setlabel(0x7310, "NORMLEFT(*X,A)")
p.setlabel(0x7326, "NORM(SX,SY)")
p.setlabel(0x7356, "SY=0.0()")
p.setlabel(0x7363, "NORM(SY)")
p.setlabel(0x73ca, "LED_ERR(A)")
p.setlabel(0x76e6, "ERR1_UNDEF_CMDa")
p.setlabel(0x76f9, "RESULT_TO_GPIB()")
p.setlabel(0x7716, "LED_TO_GPIB()")
p.setlabel(0x7bd7, "HPIB_SEND(*X,A)")
p.setlabel(0x7c17, "HPIB_RECV(*X,A)")
p.setlabel(0x7d19, "ERR1_UNDEF_CMDb")
p.setlabel(0x7f6b, "LAMP_TEST()")
#######################################################################

if False:
	fx = open("/tmp/_.dot", "w")

	fx.write("""
	digraph {
	""")

	def xxx(t, p, l):
		if t.tag != "run":
			return
		s = "ellipse"
		for i in t.a['flow_in']:
			if i[0] == "call":
				s = "box"
		fx.write("N%x [shape=%s]\n" % (t.start, s))
		for i in t.a['flow']:
			if i[0] == "ret":
				fx.write("R%x [shape=hexagon,label=RET]\n" % t.start)
				fx.write("N%x -> R%x\n" % (t.start, t.start))
			if i[2] != None:
				c = "black"
				if i[0] == "call":
					c = "green"
				fx.write("N%x -> N%x [color=%s]\n" % (t.start, i[2], c))

	xnmi.recurse(xxx, p)

	fx.write("""
	}
	""")


def build_func(p, a):
	done = dict()
	todo = dict()
	l = list()

	print("BUILD_FUNC %x" % a)
	t = p.t.find(a, "run")
	done[a] = t
	sa = t.start
	ea = t.end
	y = t
	while True:
		if y.start < sa:
			print("FAIL start before entry %x < %x" % (y.start, sa), y)
			return
		if y.end > ea:
			ea = y.end
		for i in y.a['flow']:
			if i[0] == "call":
				continue
			if i[2] == None:
				continue
			if i[2] in done:
				continue
			if i[2] in todo:
				continue
			todo[i[2]] = True
			l.append(i[2])
		for i in y.a['flow_in']:
			if i[0] == "call" and y.start == sa:
				continue
			if i[2] == None:
				print("NB flow_in <none>", i)
				continue
			if i[2] < sa:
				print("NB flow_in before entry %x < %x" % (i[2], sa), i)
				continue
			if i[2] > ea:
				ea = i[2]
		if len(l) == 0:
			break
		xa = l.pop()
		del todo[xa]
		y = p.t.find(xa, "run")
		done[xa] = y
	print("COMPLETE %x..%x" % (sa, ea))
	x = p.t.add(sa, ea, "proc")
	x.blockcmt += "Procedure %x..%x\n" % (sa, ea)
	for i in x.child:
		if not i.start in done:
			print("ORPHAN", i)
	print("")

build_func(p, 0x7fe9)
build_func(p, 0x7f79)
build_func(p, 0x72d3)

# Tail-recursion resolution candidates:
#build_func(p, 0x71fa)
#build_func(p, 0x7173)

#xnmi.recurse()

p.render("/tmp/_hp5370b")
