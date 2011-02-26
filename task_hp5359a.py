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
# HP53xx EPROM structure
hp53xx.eprom(p, 0x6000, 0x8000, 0x400)

#----------------------------------------------------------------------
#
#hp53xx.nmi_debugger(p, p.m.w16(0x7ffc))

hp53xx.chargen(p)
hp53xx.wr_test_val(p)

#----------------------------------------------------------------------

for ax in range(0x703d,0x708f,2):
	const.w16(p, ax)
	p.todo(p.m.w16(ax), p.cpu.disass)

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

for ax in range(0x6225,0x624d,2):
	const.txtlen(p, ax, 2)

ncmd = 0x1d
t1 = 0x624d
t2 = t1 + ncmd * 2

x = p.t.add(t1, t2, "tbl")
x.blockcmt += "\n-\nHPIB CMD Table\n\n"

x = p.t.add(t2, t2 + ncmd * 2, "tbl")
x.blockcmt += "\n-\nHPIB command function Table\n\n"

for ax in range(0, ncmd * 2, 2):
	const.txtlen(p, t1 + ax, 2)
	if p.m.rd(t1 + ax + 1) == 0:
		sx = p.m.ascii(t1 + ax, 1)
	else:
		sx = p.m.ascii(t1 + ax, 2)

	if sx in hp5359_cmds:
		ssx = " " + hp5359_cmds[sx]
	else:
		ssx = " ?"

	x = const.w16(p, t2 + ax)
	wx = p.m.w16(t2 + ax)

	x.cmt += ("CMD_" + sx + ssx,)

	p.todo(wx, p.cpu.disass)
	p.setlabel(wx, "CMD_" + sx + ssx)

#----------------------------------------------------------------------
# SWI jmp's to X

# @609d
p.todo(0x6355, p.cpu.disass)

#----------------------------------------------------------------------

p.setlabel(0x6641, "A=OR(SX.m)")
p.setlabel(0x7394, "A=(X+A)")
p.setlabel(0x60f6, "HPIB_SEND(*X,A)")
p.setlabel(0x6a4e, "MAIN_LOOP()")

#######################################################################
if True:
	while p.run():
		pass

	p.build_bb()
	p.eliminate_trampolines()
	p.build_procs()
	p.render("/tmp/_hp5359a")
	#p.t.recurse()
	exit(0)
