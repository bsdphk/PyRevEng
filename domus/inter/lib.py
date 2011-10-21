#!/usr/local/bin/python
#
# When we disassemble "INTER" programs, we run into calls to code procedures.
# We need to divine which arguments these take, in order to proceed correctly.
#
# This file encapsulates this mess.

def pure_guess(p, inter, ins, arg):
	"""
	Simply tally up TAKEV and TAKEA calls in what we think
	is the code-procedure body.  This works surprisingly well.
	"""
	proc = p.a['procdesc']
	amax = proc - inter.gc_max
	a0 = p.m.rd(proc - arg)
	for i in range(1, inter.gc_max):
		if i == arg:
			continue
		ax = p.m.rd(proc -i)
		if ax < amax and ax > a0:
			amax = ax
	l = list()
	for i in range(a0, amax):
		v = p.m.rdqual(i)
		if v != 1:
			continue
		v = p.m.rd(i)
		if v == 0o006236:
			l.append("A")
		elif v == 0o006237:
			l.append("V")
		elif v == 0o002235:
			break
	print("Pure Guess: Codeproc %d:" % arg)
	print("  ", p.m.afmt(a0), "...", p.m.afmt(amax))
	print("  ", l)
	return l

def ident_gc(p, inter, ins, arg):
	print("IGC", arg, ins)
	if arg > inter.gc_max:
		inter.gc_max = arg
	l = pure_guess(p, inter, ins, arg)
	return l
