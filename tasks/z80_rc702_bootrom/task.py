#!/usr/local/bin/python
#
# This is a demo-task which disassembles the "ROA375" bootrom from a
# RC702 "Piccolo" CP/M computer
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
import cpus.z80

#######################################################################
# Set up the memory image
m0 = mem.byte_mem(0, 0x10000, 0, True, "little-endian")

m0.fromfile("EPROM_ROA_375.bin", 0x0000, 1)
m0.bcols=4


#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m0)

#######################################################################
# Copy to ram position

for i in range(0x0069, 0x0800):
	y = m0.rd(i)
	d = 0x7000 + i - 0x0069
	m0.setflags(d, None,
	    m0.can_read|m0.can_write,
	    m0.invalid|m0.undef)
	m0.wr(d, y)

t = p.t.add(0x0068,0x0800,"hide")
t.render = "// Moved to 0x7000"
t.fold = True

#######################################################################

p.t.blockcmt += """-
-
"""

#const.fill(p, mid=0x8f5)

#######################################################################
cpu = cpus.z80.z80(p)

cpu.io_port[0x00] = "DISP_PARAM"
cpu.io_port[0x01] = "DISP_CMD"

cpu.io_port[0x04] = "FLOP_STATUS"
cpu.io_port[0x05] = "FLOP_DATA"

cpu.io_port[0x08] = "SIO2_DATA_A"
cpu.io_port[0x09] = "SIO2_DATA_B"
cpu.io_port[0x0a] = "SIO2_CTRL_A"
cpu.io_port[0x0b] = "SIO2_CTRL_B"

cpu.io_port[0x0c] = "CTC_0_SIOA"
cpu.io_port[0x0d] = "CTC_1_SIOA"
cpu.io_port[0x0e] = "CTC_2_INT_DISP"
cpu.io_port[0x0f] = "CTC_3_INT_FLOP"

cpu.io_port[0x10] = "PIO_KBD_DATA"
cpu.io_port[0x11] = "PIO_PARALLEL_DATA"
cpu.io_port[0x12] = "PIO_KBD_CTRL"
cpu.io_port[0x13] = "PIO_PARALLEL_CTRL"


cpu.io_port[0x14] = ("DIP_SWITCH", "FLOP_MOTOR")

cpu.io_port[0x18] = "DISABLE_EPROM"

cpu.io_port[0x1c] = "SOUND"

for i in range(0xf0, 0x100):
	cpu.io_port[i] = "DMA_%02x" % i

#######################################################################

cpu.disass(0)
cpu.disass(0x0027)

#######################################################################
# Interrupt vectors

for i in range(0x7300,0x7320, 2):
	da = p.m.l16(i)
	cpu.disass(da)
	const.w16(p, i)

#######################################################################

while p.run():
	pass

#######################################################################

cpu.to_tree()

#######################################################################

p.setlabel(0x7000, "Error_No_System_Files")
const.txtlen(p, 0x707d, 0x15)
# p.setlabel(0x707d, '"**NO SYSTEM FILES**"')

#######################################################################

p.setlabel(0x701e, "Error_No_Diskette_Nor_Lineprog")
const.txtlen(p, 0x7092, 0x1e)
#p.setlabel(0x7092, '"**NO DISKETTE NOR LINEPROG**"')

#######################################################################

p.setlabel(0x700f, "Error_No_Katalog")
const.txtlen(p, 0x70b0, 0x10)
#p.setlabel(0x70b0, '"**NO KATALOG**"')

#######################################################################

p.setlabel(0x7068, "memcpy(BC,DE,HL)")
p.setlabel(0x70e9, "InitHW")

#######################################################################

x = p.t.add(0x7300, 0x7320, "tbl")
x.blockcmt = """-
Interrupt Vector Table
"""
p.setlabel(0x7300, "IntVectors")
p.setlabel(0x73c6, "IntVecNop")
for i in range(0x7300,0x7320,2):
	da = p.m.l16(i)
	if da == 0x73c6:
		continue
	p.setlabel(da, "IntVec%d" % ((i - 0x7300)/2))

p.setlabel(0x7362, "INT6")
p.setlabel(0x7770, "INT7")

#######################################################################

p.setlabel(0x73de, "Msg_Diskette_Error")
const.txtlen(p, 0x73f0, 0x13)

#######################################################################
const.txtlen(p, 0x7071, 0x06)
#######################################################################
const.txtlen(p, 0x7077, 0x06)
#######################################################################
const.txtlen(p, 0x70c3, 0x05)
const.txtlen(p, 0x70c8, 0x05)

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

if False:
	import pseudo

	regs = dict()
	regs["rc"] = 1
	regs["ra"] = 4
	for i in range(0,16):
		regs["r%d" %i] = 4
	regs["rsrc"] = 8
	regs["rdcl"] = 11

	def fbb(tree, priv, lvl):
		if tree.tag == "bb":
			pseudo.pseudo_test(tree, regs)

	p.t.recurse(fbb)

#######################################################################
# Render output

print("Render")
r = render.render(p)
r.add_flows()
r.render("/tmp/_.z80.txt")
