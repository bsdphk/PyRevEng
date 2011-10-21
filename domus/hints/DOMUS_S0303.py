#!/usr/local/bin/python

import domus.desc
import domus.const

def hint(p):
	p.m.hex = True
	cpu = p.c["domus"]

	p.a['page_base'] = 0x137a
	domus.desc.pagedesc(p, 0x1007, cpu.disass)
	for pg in range(3, 20):
		aa = p.a['page_base'] + pg * 0x100
		domus.const.word(p, aa)
		print(pg, aa)
		x = p.t.add(aa, aa + 0x100, "page %d" % pg)

	for c in range(0,19):
		aa = 0x1d90 + 5 * c
		domus.const.word(p, aa)
		domus.const.dot_txt(p, aa + 1, aa + 4)
		domus.const.word(p, aa + 4)
		nw = p.m.rd(aa)
		da = (nw & 0x7fff) + p.a['page_base']
		cpu.disass(da)
