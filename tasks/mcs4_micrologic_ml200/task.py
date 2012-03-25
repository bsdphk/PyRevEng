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
p.setlabel(0x6bc, "Count_Down()")
x = p.t.find(0x6bc, "ins")
x.blockcmt += """-
This is the RESET "countdown" routine

Displays:
  .9.9.9.9 9.9
  .8.8.8.8 8.8
  ...
  .0.0.0.0 0.0

It calls 0x5ca a lot, presumably to let the analog stuff settle ?

"""
#######################################################################
p.setlabel(0x7df, "Update_Display()")
x = p.t.find(0x7df, "ins")
x.blockcmt += """-
The display is driven by two chains of 3 three P4003 10-bit shift
registers, which again drives 7447 7-segment drivers.

On entry r2 contains 0x20 or 0x40, depending on which clock-pulse
line should be driven.

A total of 30 pulses are sent:

	6 x 1  Decimal points, left to right
	6 x 4  BCD to 7447, LSD to MSD order.

"""
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
r.render("/tmp/_.mcs4.txt")
