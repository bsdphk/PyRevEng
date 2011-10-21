#!/usr/local/bin/python

import domus.const as const

def hint(p):
	cpu = p.c["domus"]
	# See RCSL 43-GL-7915 p35
	pgd = p.a['progdesc']
	print("CATW", pgd)
	x = const.word(p, pgd + 7)
	x.cmt.append(" +7 First Area Process")
	x = const.word(p, pgd + 8)
	x.cmt.append(" +8 Top Area Process")
	x = const.word(p, pgd + 9)
	x.cmt.append(" +9 Head of Unit Chain")
	x = const.word(p, pgd + 10)
	x.cmt.append(" +10 Chain of Head of Unit Chain")
	a = pgd + 11
	while True:
		x = p.t.add(a, a + 20, "UnitDesc")

		x = const.word(p, a)
		x.cmt.append(" +0 Driver name reference")

		x = const.word(p, a + 1)
		x.cmt.append(" +1 Unit number")

		x = const.word(p, a + 2)
		x.cmt.append(" +2 chain")

		x = const.word(p, a + 3)
		x.cmt.append(" +3 size of unit desc")

		x = const.dot_txt(p, a + 4, a + 7)
		x = const.dot_txt(p, a + 7, a + 10)

		x = const.word(p, a + 10)
		x.cmt.append(" +10 Kit displacement")
		x = const.word(p, a + 11)
		x.cmt.append(" +11 Kit displacement")

		n = p.m.rd(a + 2)
		if n == 0:
			break
		a = n

