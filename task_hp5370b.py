#!/usr/local/bin/python
#

from __future__ import print_function

import math

import mem
import array

import tree
import pyreveng

import cpu_mc6800

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

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'" + p.m.ascii(t.start, t.end - t.start) + "'"
		return (s,)

class dot_code(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 2, "dot-code")
		p.t.add(adr, adr + 2, "dot-code", True, self)
		self.render = self.rfunc
		t = p.m.b16(adr)
		p.markbb(t, ".code")
		p.todo(t, p.cpu.disass)

	def rfunc(self, p, t, lvl):
		s = ".CODE\t%04x" % p.m.b16(t.start)
		return (s,)

class dot_ptr(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 2, "dot-ptr")
		p.t.add(adr, adr + 2, "dot-ptr", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".PTR\t%04x" % p.m.b16(t.start)
		return (s,)

class dot_float(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 7, "dot_float")
		p.t.add(adr, adr + 7, "dot-float", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".FLOAT\t%s" % nbr_render(p, t.start)
		return (s,)

dn="/rdonly/Doc/TestAndMeasurement/HP5370B/Firmware/"

m = mem.byte_mem(0, 0x10000, 0, True)
m.bcols = 3
p = pyreveng.pyreveng(m)
p.cmt_start = 48
p.cpu = cpu_mc6800.mc6800()

# The HP5370B inverts the address bus, so start at the end and count down:
p.m.fromfile(dn + "HP5370B.ROM", 0x7fff, -1)

#########
p.t.blockcmt += """
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

		0x00b7:
			0b....X...: SE[12]
			0b......X.: SA[12]
			0b.......X: SO[12]
		0x00bc:
			0b...XX...: IN[14]
		0x00f4:
			0bX.......: TB[01]

		0x0140-0x014f:	Led buffer
			0bX.......: DP
			0b....XXXX: BCD

0x4000-?	Possibly Service/Expansion EPROM
0x6000-0x7fff	EPROMS
				
"""

# 0x6f00...0x7000 = x^2/256 table

dot_float(p, 0x614c)
dot_float(p, 0x619c)
dot_float(p, 0x61a3)
dot_float(p, 0x69dd)
dot_float(p, 0x69e4)


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

for i in range(0x6000,0x8000,0x400):
	j = 0
	for jj in range(2, 0x400):
		j += p.m.rd(i + jj)
	j &= 0xffff
	j ^= p.m.b16(i)
	if j == 0xffff:
		j = "OK"
	else:
		j = "BAD"
	x = dot_word(p, i)
	x.cmt.append("EPROM checksum (%s)" % j)
	x = dot_byte(p, i + 2)
	x.cmt.append("EPROM number")
	n = 0
	for a in range(i - 1, 0x6000, -1):
		if p.m.rd(a) != 0xff:
			break;
		n += 1
	if n > 0:
		x = p.t.add(i - n, i, "fill")
		x.render = ".FILL\t%d, 0xff" % n

#######################################################################
x = p.t.add(0x7eed, 0x7ef9, "tbl")
x.blockcmt += "Write test byte values (?)\n"
for i in range(x.start, x.end):
	dot_byte(p, i)

#######################################################################
# CPU vectors
dot_code(p, 0x7ffe)
dot_code(p, 0x7ffc)
dot_code(p, 0x7ffa)
dot_code(p, 0x7ff8)

#######################################################################
# jmp table, see 7962->6054->63ec
for i in range(0x6403,0x6409,2):
	dot_ptr(p, i)
for i in range(0x640c,0x644c,2):
	dot_code(p, i)
for i in range(0x64ac,0x64c4,2):
	dot_code(p, i)
# jmp table
for i in range(0x6848,0x6858,2):
	dot_code(p, i)

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
# Table of HPIB numeric arg ranges
# & pointer into command dispatch table
#
hpib_numcmds = 14

ba = p.m.b16(0x6405)

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

p.setlabel(0x6064, "Delay(X)")
p.setlabel(0x608d, "LED_BLANK()")
p.setlabel(0x608f, "LED_FILL(A)")
p.setlabel(0x623e, "ERR4_PLL_UNLOCK")
p.setlabel(0x6244, "LedFillMinus()")
p.setlabel(0x624d, "ERR2_TI_OVERRANGE")
p.setlabel(0x62cf, "LED=LEDBUF()")
p.setlabel(0x6344, "X+=A()")
p.setlabel(0x63df, "ERR3_UNDEF_ROUTINE")
p.setlabel(0x66ea, "ERR5_UNDEF_KEY")
p.setlabel(0x7048, "PUSH(?*X)")
p.setlabel(0x705c, "*X=SX")
p.setlabel(0x7069, "memcpy(*0xae,*0xac,7)")
p.setlabel(0x707d, "Swap(SX,SY)")
p.setlabel(0x708c, "DUP()")
p.setlabel(0x70ab, "DROP()")
p.setlabel(0x70ef, "SY.m+=SX.m()")
p.setlabel(0x7115, "A=OR(SX.m)")
p.setlabel(0x7122, "A=OR(SY.m)")
p.setlabel(0x714b, "SY.m-=SX.m()")
p.setlabel(0x72fb, "NORMRIGHT(*X,A)")
p.setlabel(0x7310, "NORMLEFT(*X,A)")
p.setlabel(0x73ca, "LED_ERR(A)")
p.setlabel(0x76e6, "ERR1_UNDEF_CMDa")
p.setlabel(0x7d19, "ERR1_UNDEF_CMDb")
#######################################################################
p.render()
#p.t.recurse()
