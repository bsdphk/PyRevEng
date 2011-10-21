#!/usr/local/bin/python

import domus.const as const
import domus.desc as desc

def hint(p):
	cpu = p.c["domus"]

	#p.todo(0o20550, cpu.disass)
	#p.todo(0o14341, cpu.disass)
	desc.zonedesc(p, 0o11634)
	x = p.t.add(0o012461, 0o012474, "Func")
	x = p.t.add(0o012474, 0o012477, "Func")
	x = p.t.add(0o012477, 0o012512, "Func")
	x = p.t.add(0o013272, 0o013303, "Func")

	const.dot_txt(p, 0o012517, None)

	def do_list(p,a, nw):
		while True:
			x = p.t.add(a - 4, a + nw, "XXXTBL")
			const.dot_txt(p, a - 4, a)
			for i in range(0,nw):
				const.word(p, a + i, "%o")
			n = p.m.rd(a)
			if n == 0:
				break
			a = n

	do_list(p, 0o016451, 2)
	do_list(p, 0o026100, 4)
	do_list(p, 0o026270, 4)

	for a in range(0o015673, 0o015706):
		p.todo(p.m.rd(a), cpu.disass)
		

	a = 0o12526
	while True:
		x = p.t.add(a, a + 5, "XXXTBL")
		const.dot_txt(p, a + 2, a + 5)
		p.todo(p.m.rd(a + 1), cpu.disass)
		const.word(p, a, "%o")
		const.word(p, a + 1, "%o")
		n = p.m.rd(a)
		if n == 0:
			break;
		a = n + 2

	# calls to 20574'
	p.todo(0o20716, cpu.disass)
	p.todo(0o14600, cpu.disass)

	p.todo(0o17343, cpu.disass)

	p.todo(0o17341, cpu.disass)
	p.todo(0o015271, cpu.disass)
