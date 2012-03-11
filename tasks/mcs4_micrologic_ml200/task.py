#!/usr/local/bin/python
#
# This is a demo-task which disassembles the MicroLogic ML200 Loran-C
# Receiver
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
import cpus.mcs4


#######################################################################
# Set up the memory image
m0 = mem.byte_mem(0, 0x001000, 0, True, "little-endian")

m0.fromhexfile("P8316.hex", 0x0000, 1)
for i in range(0x800, 0x0900, 0x100):
	m0.fromhexfile("P1702.hex", i, 1)
m0.bcols=2

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m0)

#######################################################################

p.t.blockcmt += """-
-
"""


const.fill(p, mid=0x198)
const.fill(p, mid=0x6e7)
const.fill(p, mid=0x7ff)
const.fill(p, mid=0x80f)
const.fill(p, mid=0x8f5)

#######################################################################
cpu = cpus.mcs4.mcs4(p)

#######################################################################

cpu.disass(0)

#######################################################################

while p.run():
	pass

#######################################################################

cpu.to_tree()

#######################################################################

for a in range(0x66a, 0x676, 3):
	w = p.m.l16(a)
	x = const.byte(p, a, len=3, fmt="%d")
	p.setlabel(a, "CONST_%d" % w)

p.setlabel(0x6e8, "rr0++")

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
r.render("/tmp/_.mcs4.txt")
