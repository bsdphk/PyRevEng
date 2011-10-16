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
const.txt(p, 0x08)
const.txt(p, 0x25)
const.txt(p, 0x22f)
const.txt(p, 0x0d44)
const.txt(p, 0x0d60)
const.txt(p, 0x1216)
const.txt(p, 0x1332)

p.cpu.disass(p, 0x70)

while p.run():
	pass

r = render.render(p)
r.render("/tmp/_z8k", 0, 0x4000)
