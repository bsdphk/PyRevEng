#!/usr/local/bin/python
#

from __future__ import print_function

import cpus.nova
import domus.syscall as domus_syscall

class cpu(cpus.nova.nova):
	def __init__(self, p):
		cpus.nova.nova.__init__(self, p, "domus")
		dir = __file__[:__file__.rfind('/')]
		self.root.load(dir + "/domus_funcs.txt")
		self.p.loadlabels(dir + "/domus_page_zero.txt")

	def finish_ins(self, ins):
		if ins.mne == "INTPRETE":
			ins.flow("cond", "T", None)

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
