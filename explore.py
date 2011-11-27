#!/usr/local/bin/python
#
# Various helper functions for explorations
#

#----------------------------------------------------------------------
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#----------------------------------------------------------------------
# XXX: we could return a list of candidates sorted by gain and then
# XXX: pass it in for next iteration of brute-force

def gain(p, cpu, adr):
	while p.run():
		pass;

	ccpu = cpu.clone()
	#try:
	if True:
		ccpu.disass(adr)
		while p.run(): pass
	#except:
	else:
		print("FAIL", ccpu)
		ccpu.fails = None

	assert cpu.fails != None

	if ccpu.fails != 0:
		return None

	return ccpu.ins

def best_place_to_start(p, cpu, lo=None, hi=None):
	"""
	Try to find the instruction that causes most other instructions
	to be disassembled. 
	"""

	while p.run():
		pass;

	ref = len(cpu.ins)
	best = ref
	cand = None
	bdict = dict()

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
				if l > ref:
					lx.append(i)
				if  l > best:
					print("Best so far: ", p.m.afmt(i), l - ref)
					sys.stdout.flush()
					best = l
					cand = i
					bdict =this
			i += 1
	if cand == None:
		return (None, 0, None)
	return (cand, best - ref, lx)

#----------------------------------------------------------------------
#

def brute_force(p, cpu, lo=None, hi=None, max = None):
	"""
	Disassemble as much as possible, with as few pivot points as
	possible.  Pivot instructions are marked with a lcmt.
	"""
	n = 0

	cand, j,lx = best_place_to_start(p, cpu, lo, hi)
	if j == 0:
		return

	while True:
		print("Doing", p.m.afmt(cand), "gain", j, "list", len(lx))
		x = cpu.disass(cand)
		x.lcmt("<==== Brute Force Discovery #%d" % n)
		while p.run():
			pass;
		n += 1
		if max != None and n >= max:
			break

		ref = len(cpu.ins)
		best = ref
		cand = None
		ly = list()
		for i in lx:
			this = gain(p, cpu, i)
			if this == None:
				continue
			l = len(this)
			if l <= ref:
				continue
			ly.append(i)
			if l > best:
				#print("Best so far: ", p.m.afmt(i), l - ref)
				best = l
				cand = i
		if cand == None:
			break
		lx = ly
		j = best - ref
			
