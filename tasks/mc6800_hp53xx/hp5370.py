#!/usr/local/bin/python
#
# Functions common to:
#	HP 5370A
#	HP 5370B

# PyRevEng classes
import tree
import math
import const

def chargen(p, adr):
	for a in range(adr, adr + 16):
		const.seven_segment(p, a)
	p.setlabel(adr, "CHARGEN")

#######################################################################
#

def keyboard_dispatch(p, cpu, adr = 0x7962):
	assert p.m.rd(adr) == 0xce
	assert p.m.rd(adr + 3) == 0x7e
	ptr = p.m.b16(adr + 1)

	ii = cpu.disass(adr + 3, "ins")

	const.ptr(p, ptr, 2)
	tbl = p.m.b16(ptr)

	aa = tbl
	xx = dict()
	for col in range(8,0,-1):
		p.setlabel(aa, "Keyboard_Column_%d" % col)
		for row in range(1,5):
			x = const.ptr(p, aa, 2)
			dd = p.m.b16(aa)
			cpu.disass(dd)
			if dd not in xx:
				ii.flow("call", "XFUNC", dd)
				xx[dd] = True
			aa += 2
	x = p.t.add(tbl, aa, "tbl")
	x.blockcmt += "-\nDispatch table for Keyboard commands\n"

	p.setlabel(p.m.b16(tbl + 4), "KEY_Ext_Arm")
	p.setlabel(p.m.b16(tbl + 6), "KEY_UNDEF")
	p.setlabel(p.m.b16(tbl + 10), "KEY_Ext_Hold_Off")
	p.setlabel(p.m.b16(tbl + 14), "KEY_Reset")

#######################################################################
# List of two-letter HPIB commands
#

def hpib_cmd_table(p, adr, len = 26):
	p.hpib_cmd = list()
	x = p.t.add(adr, adr + 2 * len, "cmd-table")
	x.blockcmt += "-\nTable of two-letter HPIB commands\n"
	for i in range(adr, adr + 2 * len, 2):
		const.txtlen(p,i,2)
		p.hpib_cmd.append([p.m.ascii(i, 2),])

def hpib_arg_range(p, adr, len = 14):
	x = p.t.add(adr, adr + len * 2, "arg-range")
	x.blockcmt += "-\nTable of legal range of numeric argument for HPIB cmd"
	for i in range(0, len):
		aa = adr + i * 2
		x = const.byte(p, aa, 2)
		l = p.m.rd(aa)
		h = p.m.rd(aa + 1)
		x.lcmt(p.hpib_cmd[i][0] + "[%d-%d]" % (l,h))
		p.hpib_cmd[i].append(l)
		p.hpib_cmd[i].append(h)

def hpib_tbl_idx(p, adr):
	aa = adr
	for i in p.hpib_cmd:
		if len(i) == 1:
			break
		x = const.byte(p, aa)
		i.append(p.m.rd(aa))
		x.lcmt(i[0])
		aa += 1
	x = p.t.add(adr, aa, "idx-table")
	x.blockcmt += "-\nIndex into cmd table, add numeric arg"

def dispatch_table_arg(p, adr, cpu):
	assert p.m.rd(adr) == 0xce
	assert p.m.rd(adr + 3) == 0x7e
	ptr = p.m.b16(adr + 1)
	ii = cpu.disass(adr + 3, "ins")

	const.ptr(p, ptr, 2)
	tbl = p.m.b16(ptr)
	
	aa = tbl
	xx = dict()
	for i in p.hpib_cmd:
		if len(i) == 1:
			break
		for j in range(i[1], i[2] + 1):
			x = const.ptr(p, aa, 2)
			y = i[0] + "%d" % j
			dd = p.m.b16(aa)
			cpu.disass(dd)
			if dd not in xx:
				ii.flow("call", "XFUNC", dd)
				xx[dd] = True
			p.setlabel(dd, "CMD_" + y + "_" + gpib_expl[y])
			aa += 2
	x = p.t.add(tbl, aa, "idx-table")
	x.blockcmt += "-\nDispatch table for HPIB cmds with arg"

def dispatch_table_noarg(p, adr, cpu):
	assert p.m.rd(adr) == 0xce
	assert p.m.rd(adr + 3) == 0x7e
	ptr = p.m.b16(adr + 1)
	ii = cpu.disass(adr + 3, "ins")

	const.ptr(p, ptr, 2)
	tbl = p.m.b16(ptr)
	
	aa = tbl
	xx = dict()
	for i in p.hpib_cmd:
		if len(i) > 1:
			continue
		x = const.ptr(p, aa, 2)
		y = i[0]
		dd = p.m.b16(aa)
		cpu.disass(dd)
		if dd not in xx:
			ii.flow("call", "XFUNC", dd)
			xx[dd] = True
		p.setlabel(dd, "CMD_" + y + "_" + gpib_expl[y])
		aa += 2
	x = p.t.add(tbl, aa, "idx-table")
	x.blockcmt += "-\nDispatch table for HPIB cmds without arg\n"


# Explanation of the HP5370[AB] HPIB Commands
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

class float(tree.tree):
	def __init__(self, p, adr):
		tree.tree.__init__(self, adr, adr + 7, "dot_float")
		p.t.add(adr, adr + 7, "dot-float", True, self)
		self.render = self.rfunc
		self.nbr = float_render(p, adr)
		self.a['const'] = "FP=" + self.nbr

	def rfunc(self, p, t):
		s = ".FLOAT\t%s" % self.nbr
		return (s,)


###########################################################

def dsp_dispatch(p, cpu, adr = 0x683b):
	assert p.m.rd(adr) == 0xce
	assert p.m.rd(adr + 3) == 0xbd
	tbl = p.m.b16(adr + 1)
	ii = cpu.disass(adr + 3)

	p.setlabel(tbl, "DSP_FUNC_TABLE")
	x=p.t.add(tbl, tbl + 8 * 2, "tbl")
	x.blockcmt += "-\nTable of display functions\n"
	dspf= ("AVG", "STD", "MIN", "MAX", "REF", "EVT", "DS6", "ALL")
	j=0
	for i in range(tbl, tbl + 8 * 2, 2):
		x = const.ptr(p, i, 2)
		w = p.m.b16(i)
		p.setlabel(w, "DSP_" + dspf[j])
		ii.flow("call", "DSPFUNC", w)
		cpu.disass(w)
		j += 1

