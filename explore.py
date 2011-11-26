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
			try:
				ccpu = cpu.clone()
				ccpu.disass(i)
				while p.run():
					pass
				this = len(ccpu.ins)
				if ccpu.fails == 0 and this > best:
					best = this
					cand = i
			except:
				pass
			i += 1
	if cand == None:
		return (None, 0)
	print(p.m.afmt(cand), "is best place to start, develops %d" % (best - ref), cpu.name, "instructions")
	return (cand, best - ref)

#----------------------------------------------------------------------
#

def brute_force(p, cpu, lo=None, hi=None, max = None):
	"""
	Disassemble as much as possible, with as few pivot points as
	possible.  Pivot instructions are marked with a lcmt.
	"""
	n = 0
	while True:
		i, j = best_place_to_start(p, cpu, lo, hi)
		if j == 0:
			break
		x = cpu.disass(i)
		x.lcmt("<==== Brute Force Discovery #%d" % n)
		n += 1
		if max != None and n >= max:
			break
