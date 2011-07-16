#!/usr/local/bin/python3.2

import mem
import pyreveng

import cpu_cdp1802

m = mem.byte_mem(0,0x10000, 0, True, "big-endian")

m.bcols = 3

p = pyreveng.pyreveng(m)
p.cmt_start = 56
p.m.fromfile("cdp1802.bin", 0x0000, 1)
p.cpu = cpu_cdp1802.cdp1802()

p.cpu.vectors(p)

# Subr R(4)
p.todo(0x0644, p.cpu.disass)
x = p.t.add(0x0644,0x0654, "subr")
p.setlabel(0x0644, "SUBR R(4)")

# Subr R(5)
p.todo(0x0654, p.cpu.disass)
x = p.t.add(0x0654,0x0661, "subr")
p.setlabel(0x0654, "SUBR R(5)")

p.setlabel(0x06b9, "R15 = (R13++)")
p.setlabel(0x06be, "(R13++) = R15")
p.setlabel(0x06c5, "R15 = -R15")

while p.run():
	pass

p.build_bb()
p.build_procs()

import copy

while p.run():
	pass

p.render("/tmp/_cdp1802.bin")


