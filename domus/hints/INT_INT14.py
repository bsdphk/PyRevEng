#!/usr/local/bin/python

import domus.inter 
import domus.const as const

def hint(p):
	cpu = p.c["domus"]
	tbl_base = 0o100015

	def xx(n):
		i  = n + tbl_base
		if n in domus.inter.intins:
			x = domus.inter.intins[n]
			y = const.word(p,i)
			y.cmt.append(str(x))
			a = p.m.rd(i)
			if len(x) == 2:
				p.setlabel(a, x[1] + " **********")
			else:
				p.setlabel(a, x[1])
		x = p.m.rd(i)
		if x != 0:
			cpu.disass(x)

	for i in domus.inter.intins:
		xx(i)

