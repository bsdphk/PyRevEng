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
import cpus.mcs6500


#######################################################################
# Set up the memory image
m0 = mem.byte_mem(0, 0x010000, 0, True, "little-endian")

m0.fromfile("EPROM_Z8000_Fl.Cont._S41_6-20-85.bin", 0xe000, 1)
m0.bcols=8

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m0)

cpu = cpus.mcs6500.mcs6502(p)

for a in range(0xfffa, 0x10000, 2):
	const.w16(p, a)
	cpu.disass(p.m.l16(a))
for a in range(0xfff3, 0xfff9, 3):
	cpu.disass(a)
	pass

for a in range(0xff9a, 0xffa0, 2):
	const.w16(p, a)
	#cpu.disass(p.m.l16(a))
for a in range(0xff93, 0xff9a, 3):
	const.w16(p, a + 1)
	#cpu.disass(a)
	pass

for a in range(0xe291, 0xe29d, 2):
	da = p.m.l16(a)
	const.w16(p, a)
	cpu.disass(da)

cpu.disass(0xe034)
cpu.disass(0xe906)
cpu.disass(0xe90c)
cpu.disass(0xe90e)

cpu.disass(0xe948)
const.byte(p, 0xe962, 6)
const.byte(p, 0xe968, 5)

if False:
	cpu.disass(0xe96d)
	cpu.disass(0xe972)
	cpu.disass(0xe977)
	cpu.disass(0xe97c)
	cpu.disass(0xe989)
	cpu.disass(0xe98e)
	cpu.disass(0xe993)
	# cpu.disass(0xea33)
	cpu.disass(0xeab1)
	cpu.disass(0xeafb)
	#cpu.disass(0xeb0d)
	#cpu.disass(0xeb10)
	cpu.disass(0xeb13)
	cpu.disass(0xeb40)
	cpu.disass(0xeb9f)
	cpu.disass(0xebf1)
	#cpu.disass(0xebff)
	cpu.disass(0xec16)
	cpu.disass(0xec19)

while p.run():
	pass

cpu.to_tree()

const.fill(p, mid=0xfe6d)
const.fill(p, mid=0xffc0)

#######################################################################
for a in range(0xe7bf, 0xe7d3, 4):
	const.byte(p, a, 4)

const.byte(p, 0xe675, 4)
const.byte(p, 0xe679, 4)
const.byte(p, 0xe80a, 4)
const.byte(p, 0xe28a, 4)
#######################################################################

p.setlabel(0xe048, "ram_err")
p.setlabel(0xe7d3, "delay()")

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
r.render("/tmp/_.cbm900_fd.txt")
