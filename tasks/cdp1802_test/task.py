#!/usr/local/bin/python
#
# This is a demo-task which disassembles a cdp1802 ROM image.
#
# I have no idea what this ROM image does.  It is from a PCB I found in a
# scrap-heap many years ago.
#
# The CDP1802 is a very challenging CPU to disassemble, because of the
# indirect register PC.   We are not doing a very good job of it yet.

#######################################################################
# Check the python version
import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#######################################################################
# Set up a search path to two levels below
# XXX: There must be a better way than this gunk...
import os
sys.path.insert(0, "/".join(os.getcwd().split("/")[:-2]))

#######################################################################
# Stuff we need...
import mem
import pyreveng
import topology
import render
import cpus.cdp1802

#######################################################################
# Set up the memory image
m = mem.byte_mem(0,0x800, 0, True, "big-endian")
m.fromfile("cdp1802.bin", 0x0000, 1)
m.bcols = 3

#######################################################################
# Instantiate pyreveng instance
p = pyreveng.pyreveng(m)

#######################################################################
# Instantiate a disassembler
cpu = cpus.cdp1802.cdp1802(p)

#######################################################################
# Provide hints for disassembly
cpu.vectors(p)

# Subr R(4)
cpu.disass(0x644)
x = p.t.add(0x0644,0x0654, "subr")
p.setlabel(0x0644, "SUBR R(4)")

# Subr R(5)
cpu.disass(0x654)
x = p.t.add(0x0654,0x0661, "subr")
p.setlabel(0x0654, "SUBR R(5)")

p.setlabel(0x06b9, "R15 = (R13++)")
p.setlabel(0x06be, "(R13++) = R15")
p.setlabel(0x06c5, "R15 = -R15")

#######################################################################
# Chew through what we got

while p.run():
	pass

cpu.to_tree()

#######################################################################
# Build code graph
if True:
	p.g = topology.topology(p.t)
	p.g.segment()
	p.g.setlabels(p)
	p.g.dump_dot()
	p.g.xxx(p)

#######################################################################
# Render output

r = render.render(p)
r.add_flows()
r.render("/tmp/_.cdp1802.txt")
