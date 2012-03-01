#!/usr/local/bin/python
#
# This is a demo-task which disassembles the CBM900 disk controller MCU
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
import cpus.mcs48


#######################################################################
# Set up the memory image
m0 = mem.byte_mem(0, 0x001000, 0, True, "little-endian")

m0.fromfile("MCU_WDC_U10.bin", 0x0000, 1)
m0.bcols=2

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m0)

#######################################################################

p.t.blockcmt += """-
-
"""


const.fill(p, mid=0x004)
const.fill(p, mid=0x008)
const.fill(p, mid=0x4b0)
const.fill(p, mid=0x0f3)
const.fill(p, mid=0x1f5)
const.fill(p, mid=0x2fb)
const.fill(p, mid=0x3f1)
const.fill(p, lo=0x5f5)
const.fill(p, mid=0x6fb)
const.fill(p, mid=0x7ed)

#######################################################################
cpu = cpus.mcs48.mcs48(p)

#######################################################################

# vectors
cpu.disass(0)
cpu.disass(3)
cpu.disass(7)

#######################################################################

while p.run():
	pass

#######################################################################
# Jump table

j = cpu.disass(0x3f)
for i in range(0x0a,0x21):
	v = p.m.rd(i)
	const.byte(p, i)
	cpu.disass(v)
	j.flow("cond", "x", v)
	p.setlabel(v, "CMD_%02x" % (i - 0xa))

#######################################################################
# No idea...

for i in range(0x000,0x800,0x100):
	cpu.disass(i + 0xfe)

#######################################################################
# Pure guess

const.txt(p, 0x5ae)
cpu.disass(0x695)
cpu.disass(0x700)
cpu.disass(0x70d)
cpu.disass(0x720)
#######################################################################

import explore
#import cProfile
#cProfile.run('explore.brute_force(p, cpu, 0xe000, 0x10000)')
#explore.brute_force(p, cpu, 0x0000, 0x0800)

while p.run():
	pass

cpu.to_tree()

#######################################################################

p.setlabel(0x0df, "rr(adr=@r1,wid=r4)")
p.setlabel(0x16f, "r2:r3=sum(0x48:0x49,0x2f:0x30)")
p.setlabel(0x1dd, "inc(adr=@R0,wid=R1)")
p.setlabel(0x2f0, "toggle_P1.7()")
p.setlabel(0x6a5, "delay(someN)")
p.setlabel(0x6b2, "memcpy(0x1d,0x35,3)")
p.setlabel(0x6b8, "memcpy(r0,r1,r6)")

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
r.render("/tmp/_.cbm900_wdcd.txt")
