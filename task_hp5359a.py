#!/usr/local/bin/python
#

from __future__ import print_function

# Python classes
import math

# PyRevEng classes
import mem
import tree
import const
import pyreveng
import hp53xx
import cpu_mc6800

#----------------------------------------------------------------------
# Set up our PyRevEng instance
#

m = mem.byte_mem(0, 0x10000, 0, True, "big-endian")
m.bcols = 3
p = pyreveng.pyreveng(m)
p.cmt_start = 56

#----------------------------------------------------------------------
# Load the EPROM image
#

p.m.fromfile(
    "/rdonly/Doc/TestAndMeasurement/HP5359/Firmware/hp5359a.rom",
    0x6000,
    1)

#----------------------------------------------------------------------
# Add a CPU instance
#

p.cpu = cpu_mc6800.mc6800()
p.cpu.vectors(p,0x8000)

#----------------------------------------------------------------------

p.t.blockcmt += """

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

	
	0x0080-0x0087	SW	X X X X X X X X
	0x0088-0x008f	SZ	X X X X X X X X
	0x0090-0x0097	SY	m m m m m m m X
	0x0098-0x009f	SX	m m m m m m m X
	0x00a0-0x00a7	SA	X X X X X X X X


	0x00e2-0x0123	TEach/LearN data
			0x00e2	X		0x0012 copy
				0x20 - Output Enable
			0x00e3	X		0x0014 copy
				0x10 - Output Remote(!local)
			0x00e4	X		0x0016 copy
				0x04 - Output Normal
				0x80 - Single Cycle
			0x00e5	X
				0x04 - Output Amplitude
				0x08 - Output Offset
			0x00e6	m m m m m m m e
			0x00ee	m m m m m m m e
			0x00f6	X 
				0x01 - External Compensation Enable
				0x80 - Sync Delay Preset
			0x00f7	X 
			0x00f8	X
			0x00f9	X
				0x80 - Frequency
				0x40 - Width
				0x20 - Delay
				0x10 - Period
			0x00fa	X
			0x00fb	X
			0x00fc	X X X X X X
			0x0102	X X X X X X X X
			0x010a	X X X X X X X X
			0x0112	X X X X X X X X
			0x011a	X X X X X X X X
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
			
				
"""

p.setlabel(0x0001, "HPIB.STATUS_OUT")
p.setlabel(0x0098, "SX.m")
p.setlabel(0x009f, "SX.e")
p.setlabel(0x00e4, "COPY_16")
p.setlabel(0x0122, "COPY_2E")
p.setlabel(0x0123, "COPY_2C")
p.setlabel(0x0167, "HPIB_TX_LEN")
p.setlabel(0x0168, "HPIB_TX_PTR")
p.setlabel(0x016a, "HPIB_TX_LEN")
p.setlabel(0x016b, "HPIB_TX_PTR")

p.todo(0x616b, p.cpu.disass)
p.setlabel(0x016b, "HPIB_RX_FUNC1")
p.setlabel(0x016d, "HPIB_RX_FUNC")


p.setlabel(0x60f6, "HPIB_SEND(*X,A)")
p.setlabel(0x6123, "HPIB_RECV(*X,A,B=nowait)")
p.setlabel(0x6175, "RX_HPIB()")
p.setlabel(0x6216, "HPIBCMD(0x14+)")
p.setlabel(0x6442, "PUSH(?X)")
p.setlabel(0x6456, "(X)=SX")
p.setlabel(0x6463, "memcpy(0x00c5,0x00c3,8)")
p.setlabel(0x6465, "memcpy(0x00c5,0x00c3,B)")
p.setlabel(0x6477, "SX<->SY")
p.setlabel(0x6486, "SW=SZ,SZ=SY,SY=SX")
p.setlabel(0x649c, "SY=SX")
p.setlabel(0x64ab, "SX=SY,SY=SZ,SZ=SW")
p.setlabel(0x64b9, "SY=SZ,SZ=SW")
p.setlabel(0x64c8, "SX=0.0")
p.setlabel(0x64cb, "SX.m=0.0")
p.setlabel(0x64d7, "SX=-SX")
p.setlabel(0x6511, "SX.m+=SY.m")
p.setlabel(0x6641, "A=OR(SX.m)")
p.setlabel(0x6670, "(X).m /= 10")
p.setlabel(0x668a, "(X).m *= 10")
p.setlabel(0x6a4e, "MAIN_LOOP()")
p.setlabel(0x6ff1, "Err2_Data_Out_Of_Range()")
p.setlabel(0x7030, "HPIBCMD(-0x14 [0x0c-0x20])")
p.setlabel(0x72f1, "LED=Err(A)")
p.setlabel(0x7394, "A=(X+A)")
p.setlabel(0x73b8, "ERR=5")
p.setlabel(0x77eb, "Err9_Calibrate_Error(A)")


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
		w = p.m.w16(ax)
		x.a['EA'] = (w,)
		p.todo(w, p.cpu.disass)
	for ax in range(0x707d,0x708f,2):
		x = const.w16(p, ax)
		w = p.m.w16(ax)
		x.a['EA'] = (w,)
		p.todo(w, p.cpu.disass)


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
	x.a['EA'] = (wx,)

	p.todo(wx, p.cpu.disass)
	if p.m.rd(wx) == 0x7e:
		p.setlabel(p.m.w16(wx + 1), "CMD_" + sx + ssx)
	else:
		p.setlabel(wx, "CMD_" + sx + ssx)

#----------------------------------------------------------------------
# SWI jmp's to X

# @609d
p.todo(0x6355, p.cpu.disass)

#----------------------------------------------------------------------
#----------------------------------------------------------------------

const.w16(p, 0x68b7)
p.setlabel(0x68b7, "NUM_DIG")

#----------------------------------------------------------------------

const.byte(p, 0x7fa3, 14)
const.byte(p, 0x7fb1, 14)

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
                        
        def rfunc(self, p, t, lvl):
                s = ".FLOAT\t%s" % self.nbr
                return (s,)

dot_float(p, 0x7f03)
dot_float(p, 0x7f0b)
dot_float(p, 0x7f13)
dot_float(p, 0x7f1b)
dot_float(p, 0x7f23)
dot_float(p, 0x7f2b)
dot_float(p, 0x7f33)
dot_float(p, 0x7f3b)
dot_float(p, 0x7f43)
dot_float(p, 0x7f4b)
dot_float(p, 0x7f53)
dot_float(p, 0x7f5b)
dot_float(p, 0x7f63)
dot_float(p, 0x7f6b)
dot_float(p, 0x7f73)
dot_float(p, 0x7f7b)
dot_float(p, 0x7f83)
dot_float(p, 0x7f8b)
dot_float(p, 0x7f93)
dot_float(p, 0x7f9b)

#######################################################################
while p.run():
	pass

p.build_bb()
p.eliminate_trampolines()
p.build_procs()

#######################################################################

for ax in (0x7307, 0x730b, 0x7b90, 0x7c94, 0x7c98):
	x = p.t.find(ax, "ins")
	hp53xx.sevenseg(p, x, p.m.rd(x.start + 1))

#######################################################################

p.render("/tmp/_hp5359a")
#p.t.recurse()
exit(0)
