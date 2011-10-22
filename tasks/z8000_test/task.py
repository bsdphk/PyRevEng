#!/usr/local/bin/python
#
# This is a demo-task which disassembles a Z8000 ROM image.
#
# I belive the roms in question are the boot-roms from a
# Zilog S8000/21 UNIX computer.
#
# NB: the Z8000 disassembler is not very good yet
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
import cpus.z8000


#######################################################################
# Set up the memory image
m = mem.byte_mem(0, 0x4000, 0, True, "big-endian")
m.fromfile("u93.bin", 0, 2)
m.fromfile("u91.bin", 1, 2)
m.fromfile("u94.bin", 0x2000, 2)
m.fromfile("u92.bin", 0x2001, 2)
m.bcols=8

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m)

#######################################################################
# Instantiate a disassembler
cpu = cpus.z8000.z8000(p)

#######################################################################
# Provide hints for disassembly
const.w16(p, 0)
const.w16(p, 2)
const.w16(p, 4)
const.w16(p, 6)

cpu.disass(p.m.b16(6))

#######################################################################
# More hints...

if False:
	# Args to 0x050c and 0x12f0
	def lstr(p, a):
		const.w16(p, a)
		const.txtlen(p, a + 2, p.m.b16(a))

	lstr(p, 0x0024)
	lstr(p, 0x0d42)
	lstr(p, 0x0d98)
	lstr(p, 0x1214)
	lstr(p, 0x1228)
	lstr(p, 0x123c)
	lstr(p, 0x1250)
	lstr(p, 0x126a)

	# Args to SC(0x0c)
	lstr(p, 0x13a0)
	lstr(p, 0x13ae)

	
if False:
	# Moved to 0xf800 for exec
	x = p.t.add(0x2c68, 0x2c68 + 0xc6, "blk")
	cpu.disass(0x2c68)
	x = p.t.add(0x2d48, 0x2d48 + 0xc6, "blk")
	cpu.disass(0x2d48)

if False:
	# From 0x1544 ?
	# Looks like it's called from segmented mode ??
	cpu.disass(0x1ab8)
	
if False:
	for i in range(0, 16):
		t1 = p.m.rd(0x1b2 + i)
		t2 = p.m.b16(0x1c2 + 2 * i)
		const.w16(p, 0x1c2 + 2 * i)
		p.todo(t2, cpu.disass)
		p.setlabel(t2, "CMD_%c" % t1)

if False:
	p.setlabel(0xa68, "OUTCHAR")
	p.setlabel(0xa80, "OUTNL")

if False:
	# 0x43bc and 0x43ba pointers
	p.todo(0x0786, cpu.disass)
	p.todo(0x0766, cpu.disass)
	p.todo(0x0796, cpu.disass)
	p.todo(0x0776, cpu.disass)
		

#######################################################################
# Chew through what we got

while p.run():
	pass

cpu.to_tree()

#######################################################################
# Build code graph

if True:
	p.g = topology.topology(p)
	p.g.build_bb()
	p.g.segment()
	p.g.dump_dot()
	p.g.xxx(p)

#######################################################################
# Render output

r = render.render(p)
r.add_flows()
r.render("/tmp/_.z8000.txt")
