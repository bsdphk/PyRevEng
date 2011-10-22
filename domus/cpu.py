#!/usr/local/bin/python
#

from __future__ import print_function

import os
import mem
import cpus.nova
import domus.syscall as domus_syscall
import domus.const as const

class cpu(cpus.nova.nova):
	def __init__(self, p):
		cpus.nova.nova.__init__(self, p, "domus")
		self.dir = os.path.dirname(__file__)
		self.root.load(self.dir + "/domus_funcs.txt")
		self.p.loadlabels(self.dir + "/domus_page_zero.txt")

	def pz_entries(self):
		i = self.root.root.spec[0]
		assert i[0] == 0xffff
		pz = dict()
		for j in sorted(i[1]):
			if j & 0xf700 == 0x0400:
				k = i[1][j]
				pz[j & 0xff] = k.spec[0]
		for i in sorted(pz.keys()):
			try:
				w = self.p.m.rd(i)
				x = const.word(self.p, i)
				x.lcmt(pz[i])
				if w != 0:
					self.disass(w)
					self.p.setlabel(w, pz[i])
			except mem.MemError:
				del pz[i]

		fi = open(self.dir + "/domus_page_zero.txt", "r")
		for i in fi.readlines():
			i = i.strip()
			if i == "" or i[0] == "#":
				continue
			i = i.split()
			j = int(i[1], 0)
			if j in pz:
				print("PZ", pz[i], i)
				continue
			try:
				w = self.p.m.rd(j)
				x = const.word(self.p, j)
				x.lcmt(i[0])
			except:
				pass
		fi.close()
		
		

	def finish_ins(self, ins):
		if ins.mne == "INTPRETE":
			if "inter" in self.p.c:
				self.p.c["inter"].disass(ins.hi)
			else:
				print("\n"
				    "NOTE:  This programs uses the "
				    "DOMUS Interpreter.\n"
				    "You should load a disassembler "
				    "for this also (domus.inter.inter)"
				    "\n"
				)
				    
			ins.flow("cond", "T", None)

		w = self.p.m.rd(ins.lo)
		if w & 0xff00 == 0x0400:
			# JMP X,0 don't come back...
			ins.flow("ret", "INT", None)

		if not ins.mne in domus_syscall.doc:
			cpus.nova.nova.finish_ins(self, ins)
			return

		d = domus_syscall.doc[ins.mne]
		if type(d) == str:
			ins.lcmt(d)
		elif type(d[0]) == str:
			ins.lcmt(d[0])
		else:
			for i in d[0]:
				ins.lcmt(i)
		if type(d) != str and len(d) > 1:
			for i in range(0,len(d[1])):
				j = d[1][i]
				self.p.setlabel(ins.lo + i + 1, "." + j)
				ins.flow("cond", j, ins.lo + i + 1)

		cpus.nova.nova.finish_ins(self, ins)
