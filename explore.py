#!/usr/local/bin/python
#
# Various helper functions for explorations
#

#----------------------------------------------------------------------
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#----------------------------------------------------------------------

def gain(p, cpu, adr):
	"""
	How many instructions would we gain by starting disassembly at adr ?
	"""

	while p.run():
		pass;

	ccpu = cpu.clone()

	ccpu.disass(adr)
	while p.run():
		pass

	assert cpu.fails != None

	dx = dict()
	for i in ccpu.ins:

		# We only care for new stuff
		if i in cpu.ins:
			continue

		j = ccpu.ins[i]

		# If they are OK, we return them
		if j.status == "OK":
			dx[i] = j
			continue

		# If they failed, propagate up
		if j.status == "fail":
			j.disass = cpu
			cpu.ins[i] = j
			continue

	if ccpu.fails != 0:
		return None

	return dx

def best_place_to_start(p, cpu, lo=None, hi=None):
	"""
	Try to find the instruction that causes most other instructions
	to be disassembled. 

	Returns a list of (adr, #ins) tupples.
	"""

	while p.run():
		pass;

	best = 0
	cand = None
	bdict = dict()

	lp = 0
	lx = list()
	for g in p.t.gaps():
		g = list(g)
		if lo != None:
			if  lo >= g[1]:
				continue
			if g[0] < lo:
				g[0] = lo
		if hi != None:
			if hi <= g[0]:
				continue
			if g[1] > hi:
				g[1] = hi
		i = g[0]
		while i < g[1]:
			if i >> 12 != lp:
				print("..." + p.m.afmt(i), "cands:", len(lx))
				lp = i >> 12
			if i in cpu.ins:
				i = cpu.ins[i].hi
				continue
			if cpu.bm.tst(i):
				i += 1
				continue
			if i in bdict:
				i = bdict[i].hi
				continue
			this = gain(p, cpu, i)
			if this != None:
				l = len(this)
				if l > 0:
					lx.append((i,l))
				if  l > best:
					print("Best so far: ", p.m.afmt(i), l)
					sys.stdout.flush()
					best = l
					cand = i
					bdict =this
			i += 1
	lx = sorted(lx, key=lambda x: -x[1])
	return lx

#----------------------------------------------------------------------
#

def brute_force(p, cpu, lo=None, hi=None, max = None):
	"""
	Disassemble as much as possible, with as few pivot points as
	possible.  Pivot instructions are marked with a lcmt.
	"""
	n = 0

	lx = best_place_to_start(p, cpu, lo, hi)
	if len(lx) == 0:
		return

	cand = lx[0][0]
	j = lx[0][1]

	while True:
		print("Doing", p.m.afmt(cand), "gain", j, "list", len(lx))
		x = cpu.disass(cand)
		x.lcmt("<==== Brute Force Discovery #%d" % n)
		while p.run():
			pass;
		n += 1
		if max != None and n >= max:
			break

		lx = sorted(lx, key=lambda x: -x[1])
		best = 0
		cand = None
		ly = list()
		for j in lx:
			i,n = j
			if n < best:
				ly.append(j)
				continue
			this = gain(p, cpu, i)
			if this == None:
				continue
			l = len(this)
			if l <= 0:
				continue
			ly.append((i,l))
			if l > best:
				best = l
				cand = i
		if cand == None:
			break
		lx = ly
		j = best
			
