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
import render
import topology
import cpu_z8000


m = mem.byte_mem(0, 0x10000, 0, True, "big-endian")
m.bcols=8
p = pyreveng.pyreveng(m)
p.cmt_start = 56
p.g = topology.topology(p)

p.cpu = cpu_z8000.z8000()

p.m.fromfile("Z8k/u93.bin", 0, 2)
p.m.fromfile("Z8k/u91.bin", 1, 2)
p.m.fromfile("Z8k/u94.bin", 0x2000, 2)
p.m.fromfile("Z8k/u92.bin", 0x2001, 2)

const.w16(p, 0)
const.w16(p, 2)
const.w16(p, 4)
const.w16(p, 6)
#const.txt(p, 0x08)
#const.txt(p, 0x25)
#const.txt(p, 0x22f)
#const.txt(p, 0x0d44)
#const.txt(p, 0x0d60)
#const.txt(p, 0x1216)
#const.txt(p, 0x1332)

if True:
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

	
if True:
	# Moved to 0xf800 for exec
	x = p.t.add(0x2c68, 0x2c68 + 0xc6, "blk")
	p.cpu.disass(p, 0x2c68)
	x = p.t.add(0x2d48, 0x2d48 + 0xc6, "blk")
	p.cpu.disass(p, 0x2d48)

if True:
	# From 0x1544 ?
	# Looks like it's called from segmented mode ??
	p.cpu.disass(p, 0x1ab8)
	
p.cpu.disass(p, 0x70)

for i in range(0, 16):
	t1 = p.m.rd(0x1b2 + i)
	t2 = p.m.b16(0x1c2 + 2 * i)
	const.w16(p, 0x1c2 + 2 * i)
	p.todo(t2, p.cpu.disass)
	p.setlabel(t2, "CMD_%c" % t1)

p.setlabel(0xa68, "OUTCHAR")
p.setlabel(0xa80, "OUTNL")

if True:
	# 0x43bc and 0x43ba pointers
	p.todo(0x0786, p.cpu.disass)
	p.todo(0x0766, p.cpu.disass)
	p.todo(0x0796, p.cpu.disass)
	p.todo(0x0776, p.cpu.disass)
		

while p.run():
	pass

if True:
	p.g.build_bb()
	# p.g.add_flow("RESET", 0x70)
	p.g.segment()
	p.g.dump_dot()

	p.g.xxx(p)

r = render.render(p)
r.add_flows()
r.render("/tmp/_z8k", 0, 0x4000)
