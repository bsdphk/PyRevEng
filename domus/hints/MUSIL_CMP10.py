#!/usr/local/bin/python

import domus.const as const
import domus.desc as desc
import domus.inter.inter

def follow_chain(p, a, f = None):
	while a != 0:
		if f != None:
			f(p, a)
		x = const.word(p, a + 2)
		x.lcmt("+2 CHAIN")
		x = const.dot_txt(p, a + 4, a + 7)
		x.lcmt("+4 NAME")
		a = p.m.rd(a + 2)

def hunt_outtext(p, cpu):
	""" A very crude value tracker for system calls
	"""

	did = dict()
	for i in cpu.ins:
		ins = cpu.ins[i]
		w = p.m.rd(ins.lo)
		if w & 0xff00 != 0x0c00:
			continue

		ac = [None,None,None,None]
		x = i-1
		while x in cpu.ins:
			ins1 = cpu.ins[x]
			if ins1.mne != "LDA":
				#print("!", cpu.render(p, ins1))
				break
			if len(ins1.oper) != 2:
				#print("!", cpu.render(p, ins1))
				break
			n = int(ins1.oper[0])
			ac[n] = ins1.oper[1][0]
			const.word(p, ac[n])
			x -= 1

		if ac == [None,None,None,None]:
			continue

		s = p.m.afmt(i)
		s += " "
		s += cpu.render(p, ins)[0]
		s += "  "
		for j in range(0,4):
			i = ac[j]
			if i != None:
				s += " AC%d=" % j + p.m.afmt(i)
				try:
					w = p.m.rd(i)
					q = p.m.rdqual(i)
					s += "=" + p.m.aqfmt(w, q)
				except:
					s += "=undef"

		print(s)
		if ins.mne == "SEARCHITEM":
			if ac[1] != None:
				try:
					w = p.m.rd(ac[1])
					print("  HEAD",
					    p.m.afmt(ac[1]), p.m.afmt(w))
					const.word(p, w + 2)
				except:
					pass

			if ac[2] != None:
				w = p.m.rd(ac[2])
				print("  NAME", p.m.afmt(ac[2]), p.m.afmt(w))
				try:
					const.dot_txt(p, w, w + 3)
				except:
					pass
		if ins.mne == "SENDMESSAGE":
			if ac[1] != None:
				w = p.m.rd(ac[1])
				print("  MSG", p.m.afmt(ac[1]), p.m.afmt(w))
				for j in range(0,4):
					try:
						const.word(p, w + j)
					except:
						pass
				try:
					ww = p.m.rd(w + 2)
					q = p.m.rdqual(w + 2)
					if q == 3 and ww != 0:
						const.dot_txt(p, ww >> 1)
				except:
					pass
						
			if ac[2] != None:
				w = p.m.rd(ac[2])
				print("  DST", p.m.afmt(ac[2]), p.m.afmt(w))
				try:
					const.dot_txt(p, w, w + 3)
				except:
					pass

		if ins.mne[:3] == "OUT" or ins.mne == "OPEN":
			if ac[2] != None:
				z = p.m.rd(ac[2])
				if z in did:
					continue
				did[z] = True
				print("  ZONE", p.m.afmt(z))
				p.todo(z, desc.zonedesc)
		if ins.mne == "OUTTEXT":
			if ac[0] != None:
				t = p.m.rd(ac[0])
				if t in did:
					continue
				did[t] = True
				if t != 0:
					t = t >> 1
					print("  TXT",
					    p.m.afmt(ac[0]), p.m.afmt(t))
					try:
						const.dot_txt(p, t)
					except:
						pass


def hint(p):
	p.m.hex = True
	cpu = p.c["domus"]

	#p.todo(0o20550, cpu.disass)
	#p.todo(0o14341, cpu.disass)
	desc.zonedesc(p, 0o11634)
	x = p.t.add(0o012461, 0o012474, "Func")
	x = p.t.add(0o012474, 0o012477, "Func")
	x = p.t.add(0o012477, 0o012512, "Func")
	x = p.t.add(0o013272, 0o013303, "Func")

	const.dot_txt(p, 0o012517, None)

	def do_list(p, a, nw, fn = None):
		while a != 0:
			x = p.t.add(a - 4, a + nw, "XXXTBL")
			const.dot_txt(p, a - 4, a)
			if fn != None:
				fn(p, a)
			else:
				for i in range(0,nw):
					const.word(p, a + i, "%o")
			a = p.m.rd(a)

	do_list(p, 0o016451, 2)

	def fsym(p, a):
		l = list()
		for i in range(0, 4):
			l.append(const.word(p, a + i, "%o"))
		l[3].lcmt(str(domus.inter.inter.intins[p.m.rd(a + 3)][1:]))
			

	do_list(p, 0o026100, 4)
	do_list(p, 0o026270, 4, fsym)

	for a in range(0o015673, 0o015706):
		p.todo(p.m.rd(a), cpu.disass)

	
	def c12524(p, a):
		const.word(p, a + 3)
		cpu.disass(p.m.rd(a + 3))
	follow_chain(p, 0o12524, c12524)

	def c13055(p, a):
		const.word(p, a + 0)
		const.word(p, a + 1)
		const.word(p, a + 3)
		const.word(p, a + 7)
	follow_chain(p, 0o13055, c13055)

	# calls to 20574'
	p.todo(0o20716, cpu.disass)
	p.todo(0o14600, cpu.disass)

	p.todo(0o17343, cpu.disass)

	p.todo(0o17341, cpu.disass)
	p.todo(0o015271, cpu.disass)

	p.run()

	hunt_outtext(p, cpu)
