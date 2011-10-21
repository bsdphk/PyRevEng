#!/usr/local/bin/python

import domus.inter.inter as inter
import domus.const as const

def hint(p):
	p.m.hex = False
	cpu = p.c["domus"]
	tbl_base = 0x800d

	# "PINTGIVEUP" ?
	cpu.disass(0xa0)

	def xx(n):
		i  = n + tbl_base
		x = inter.intins[n]
		y = const.word(p,i)
		id = "op=%d: " % n + x[1] + str(x[2:])
		y.cmt.append(id)
		a = p.m.rd(i)
		if len(x) == 2:
			p.setlabel(a, x[1] + " **********")
		else:
			p.setlabel(a, x[1])
		x = p.m.rd(i)
		if x != 0:
			ins = cpu.ins[0x800c]
			ins.flow("cond", "#%d" % n, x)
			z = cpu.disass(x)
			z.lcmt(id)

	for i in inter.intins:
		xx(i)

	p.setlabel(0x1000, "TxtBreak")
	const.dot_txt(p, 0x1000, 0x1005)

	p.setlabel(0x1005, "TxtError")
	const.dot_txt(p, 0x1005, 0x100a)

	p.setlabel(0o100267, "Execute")
	p.setlabel(0o100273, "GetZoneAddr")
	p.setlabel(0o100371, "TakeAidxV")
	p.setlabel(0o100407, "Take2Addr")
	p.setlabel(0o100644, "Send2Oper")
	p.setlabel(0o100654, "_OperMsg")

	p.setlabel(0o101117, "IntGiveup")
	cpu.disass(0o101117)

	p.setlabel(0o101131, "PIntGiveup")
	cpu.disass(0o101131)

	# Empty table entries
	const.word(p, 0o100361)
	const.word(p, 0o100362)

	# Operator Message
	const.word(p, 0o100654)
	const.word(p, 0o100655)
	const.word(p, 0o100656)
	const.word(p, 0o100657)
	const.word(p, 0o100660)

	const.dot_txt(p, 0o101270, 0o101271)
	const.dot_txt(p, 0o101271, 0o101272)
	for i in range(0o101272, 0o101277):
		const.word(p, i)
	for i in (0o100325, 0o101331):
		const.word(p, i)
	const.dot_txt(p, 0o101332, 0o101333)


