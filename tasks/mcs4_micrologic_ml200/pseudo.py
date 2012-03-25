#!/usr/local/bin/python
#
# Prototype-pseudocode resolver
#

#######################################################################
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#######################################################################
# Set up a search path to two levels below

import os
sys.path.insert(0, os.path.abspath(os.path.join(".", "..", "..")))

import copy

#######################################################################
class pseudo(object):
	def __init__(self, src, dst, name):
		self.src = src
		self.dst = dst
		self.name = name

	def lcmt(self):
		return self.name + " " + str(self.src) + " -> " + str(self.dst)

	def __repr__(self):
		return self.lcmt()

	def valstr(self, vals):
		s = "("
		if type(self.dst) == str and self.dst in vals:
			s += self.dst + " = " + str(vals[self.dst])
		for i in self.src:
			if type(i) == str and i in vals:
				s += ", " + i + " = " + str(vals[i])
		return s + ")"

	def propagate_value(self, vals, regs):
		if type(self.dst) == str:
			vals[self.dst] = None
		x = self.valstr(vals)
		y = False
		for i in range(0, len(self.src)):
			j = self.src[i]
			if type(j) == int:
				y = True
			if type(j) != str:
				continue
			if j in vals and type(vals[j]) == int:
				y = vals[j]
				if j in regs:
					z = y & ((1 << regs[j]) - 1)
					if z != y:
						print("TRIM", self, j, y, z)
						y = z
				x = self.src[:i] + (y,) + self.src[i+1:]
				self.src = x
				y = True
		if y:
			r = self.vprop(vals)
			if r != None:
				x = r.vprop(vals)
				assert(x == None)
		else:
			r = None
		print("%-35s" % self.lcmt(), x, " -> ", self.valstr(vals))
		return r

	def vprop(self, vals):
		return

#######################################################################
class add(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "add")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] + self.src[1],), self.dst)
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((self.src[1],), self.dst)
		if type(self.src[1]) == int and self.src[1] == 0:
			return mov((self.src[0],), self.dst)

#######################################################################
class land(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "and")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((0,), self.dst)
		if type(self.src[1]) == int and self.src[1] == 0:
			return mov((0,), self.dst)
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] & self.src[1],), self.dst)

#######################################################################
class ldm(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "ldm")

#######################################################################
class lor(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "or")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] | self.src[1],), self.dst)
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((self.src[1],), self.dst)
		if type(self.src[1]) == int and self.src[1] == 0:
			return mov((self.src[0],), self.dst)

#######################################################################
class lsh(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "lsh")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((0,), self.dst)
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] << self.src[1],), self.dst)

#######################################################################
class mov(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "mov")

	def vprop(self, vals):
		assert len(self.src) == 1
		if type(self.src[0]) == int:
			vals[self.dst] = self.src[0]

#######################################################################
class nop(pseudo):
	def __init__(self, src = (), dst = None):
		pseudo.__init__(self, src, dst, "nop")

#######################################################################
class null(pseudo):
	def __init__(self, src = (), dst = None):
		pseudo.__init__(self, src, dst, "null")

	def lcmt(self):
		return "."

#######################################################################
class ref(pseudo):
	def __init__(self, tree, ins):
		pseudo.__init__(self, (), True, "ref")
		self.tree = tree
		self.ins = ins

	def lcmt(self):
		return self.name + " ___%03x___" % self.ins.lo + self.ins.mne + " " + str(self.ins.oper)

	def propagate_value(self, vals, regs):
		return

#######################################################################
class ret(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "ret")

#######################################################################
class rsh(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "rsh")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((0,), self.dst)
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] >> self.src[1],), self.dst)

#######################################################################
class stm(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "stm")

#######################################################################
class xor(pseudo):
	def __init__(self, src, dst):
		pseudo.__init__(self, src, dst, "xor")

	def vprop(self, vals):
		assert len(self.src) == 2
		if type(self.src[0]) == int and type(self.src[1]) == int:
			return mov((self.src[0] ^ self.src[1],), self.dst)
		if type(self.src[0]) == int and self.src[0] == 0:
			return mov((self.src[1],), self.dst)
		if type(self.src[1]) == int and self.src[1] == 0:
			return mov((self.src[0],), self.dst)


#######################################################################
class xxx(pseudo):
	def __init__(self, src = (), dst = None):
		pseudo.__init__(self, src, dst, "xxx")

#######################################################################
class zap(pseudo):
	def __init__(self, dst = None):
		pseudo.__init__(self, (), dst, "zap")

	def vprop(self, vals):
		del vals[self.dst]


#######################################################################

def propagate_values(l, regs):
	v = dict()
	ll = list()
	for i in range(0, len(l)):
		j = l[i]
		x = j.propagate_value(v, regs)
		if x != None:
			ll.append(x)
			print("XXX", j, x)
		else:
			ll.append(j)
		for i in v:
			if i in regs and type(v[i]) == int:
				x = v[i] & ((1 << regs[i])-1)
				if x != v[i]:
					print("CLIP", j, i, v[i], x)
					v[i] = x
	return ll

def dead_stores(l):
	v = dict()
	ll = list()
	for i in range(len(l)-1, -1, -1):
		j = l[i]
		jj = j
		print("D", j)
		if type(j.dst) == str:
			if j.dst in v and v[j.dst] == True:
				print("Dead", j)
				jj = null()
			v[j.dst] = True
		for k in j.src:
			if type(k) == str:
				v[k] = False
		ll.insert(0, jj)

	return ll

#######################################################################
def reduce(l, regs):
	if False:
		print("---------------------------------------")
		for i in l:
			print("R>", i)

	print("---------------------------------------")
	ll = propagate_values(l, regs)

	if False:
		print("---------------------------------------")
		for i in range(0, len(l)):
			if l[i] != ll[i]:
				print("A>", "%-35s" % l[i], "%-35s" % ll[i])
			else:
				print("A>", "%-35s" % l[i])

	if True:
		print("---------------------------------------")
		lm = dead_stores(ll)
	else:
		print("---------------------------------------")
		lm = propagate_values(ll)

	if True:
		print("---------------------------------------")
		for i in range(0, len(l)):
			if l[i] != ll[i] or ll[i] != lm[i]:
				print("A>", "%-35s" % l[i], "%-35s" % ll[i], "%-35s" % lm[i])
			else:
				print("A>", "%-35s" % "",   "%-35s" % "",    "%-35s" % l[i])
	return lm


#######################################################################
def pseudo_test(bb, regs):

	def fn(tr, priv, lvl):
		if tr.tag != "ins":
			return
		ins = tr.a['ins']
		priv.append(ref(tr, ins))
		d = dict()
		for i in ins.pseudo:
			if type(i) == tuple:
				for k in i[1]:
					if k == i[2]:
						print("XXX", ins, ins.mne, ins.pseudo)
				if type(i[2]) == str and i[2][:3] == "tmp":
					d[i[2]] = True
			if type(i.dst) == str and i.dst[:3] == "tmp":
				d[i.dst] = True
			priv.append(i)
		for i in d:
			priv.append(zap(i))

	def do_bb(x):
		l = list()
		l.append(mov((0,), 'rdcl'))
		x.recurse(func=fn, priv=l)
		l.append(zap("tmp0"))
		l.append(zap("tmp1"))
		l.append(zap("tmp2"))

		ln = reduce(l, regs)

		ln.pop(0)
		ln.pop()
		ln.pop()
		ln.pop()

		ii = None
		while len(ln) > 0:
			i = ln.pop(0)
			if i.name == "ref":
				print("I>>", i)
				ii = i.ins
				tt = i.tree
				ii.pseudo = list()
			elif ii != None:
				ii.pseudo.append(i)
				x = i.lcmt()
				if x != ".":
					tt.lcmt(x)
				

	do_bb(bb)
