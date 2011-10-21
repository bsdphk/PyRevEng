#!/usr/local/bin/python
#

from __future__ import print_function

import cpus.nova
import cpu_domus_int
import tree
import mem

import domus.syscall as domus_syscall

class word(tree.tree):
	def __init__(self, p, adr, fmt = "%d"):
		tree.tree.__init__(self, adr, adr + 1, "word")
		p.t.add(adr, adr + 1, "word", True, self)
		self.fmt = fmt
		self.render = self.rfunc

	def rfunc(self, p, t):
		try:
			x = p.m.rd(t.start)
		except:
			return ()
		q = p.m.rdqual(t.start)
		if q == 3:
			return ((".word\t" + p.m.afmt(x/2) + "*2"),)
		elif q == 2:
			return ((".word\t" + p.m.afmt(x)),)
		else:
			return ((".word\t" + self.fmt) % x, )

class dot_txt(tree.tree):
	def __init__(self, p, start, end):
		if end == None:
			end = start
			while True:
				a = p.m.rd(end)
				if a & 0xff == 0:
					break
				if a >> 8 == 0:
					break
				end += 1
		tree.tree.__init__(self, start, end, "dot_txt")
		p.t.add(start, end, "dot_txt", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t):
		s = ".TXT\t'"
		for i in range(t.start, t.end):
			q = p.m.rdqual(i)
			if q != 1:
				raise DomusError(t.start, ".TXT is relocated")
			x = p.m.rd(i)
			y = x >> 8
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
			y = x & 0xff
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
		s += "'"
		return (s,)



PageDesc = (
	( 1, "page size"),
	( 1, "page mask"),
	( 1, "blocking factor"),
	( 1, "page table"),
	( 1, "pagemap"),
	( 1, "statproc"),
	( 1, "first frame"),
	( 1, "top of frames"),
	( 1, "victim"),
	( 1, "pages read"),
	( 1, "pages written"),
	( 1, "pages in"),
	( 1, "pages out"),
	( 1, "adr input mess"),
	( 1, "input message[0]"),
	( 1, "input message[1]"),
	( 1, "input message[2]"),
	( 1, "input message[3]"),
	( 1, "adr output mess"),
	( 1, "output message[0]"),
	( 1, "output message[1]"),
	( 1, "output message[2]"),
	( 1, "output message[3]"),
	( 1, "pager flag"),
	( 1, "working locations"),
)

MsgDesc = (
	( 1, "next"),
	( 1, "prev"),
	( 1, "chain"),
	( 1, "size"),
	( 1, "sende"),
	( 1, "recei"),
	( 1, "mess0"),
	( 1, "mess1"),
	( 1, "mess2"),
	( 1, "mess3"),
)

ProgDesc = (
	( 1, "spec"),
	( 1, "start"),
	( 1, "chain"),
	( 1, "size"),
	( 3, "name"),
)

ProcDesc = (
	( 1, "next"),
	( 1, "prev"),
	( 1, "chain"),
	( 1, "size"),
	( 3, "name"),
	( 1, "first_event"),
	( 1, "last_event"),
	( 1, "buffer"),
	( 1, "program"),
	( 1, "state"),
	( 1, "timer_count"),
	( 1, "priority"),
	( 1, "break_address"),
	( 1, "ac0"),
	( 1, "ac1"),
	( 1, "ac2"),
	( 1, "ac3"),
	( 1, "psw"),
	( 1, "save"),
	( 1, "buf"),
	( 1, "address"),
	( 1, "count"),
	( 1, "reserver"),
	( 1, "conversion_table"),
	( 1, "clear_interrupt"),
)

ZoneDesc = (
	( 3, "name"),
	( 1, "size"),
	( 1, "zmode"),
	( 1, "zkind"),
	( 1, "zmask"),
	( 1, "zgive"),
	( 1, "zfile"),
	( 1, "zbloc"),
	( 1, "zconv"),
	( 1, "zbuff"),
	( 1, "zsize"),
	( 1, "zform"),
	( 1, "zleng"),
	( 1, "zfirs"),
	( 1, "ztop"),
	( 1, "zused"),
	( 1, "zshar"),
	( 1, "zrem"),
	( 1, "z0"),
	( 1, "z1"),
	( 1, "z2"),
	( 1, "z3"),
	( 1, "z4"),
	( 1, "z5"),
	( 1, "z"),
)

ShareDesc = (
	( 1, "soper" ),
	( 1, "scount" ),
	( 1, "saddr", ),
	( 1, "sspec", ),
	( 1, "snext", ),
	( 1, "sstat", ),
	( 1, "sfirs", ),
	( 1, "ssize", ),
)

class domus(cpus.nova.nova):
	def __init__(self, p):
		cpus.nova.nova.__init__(self, p, "domus")
		self.root.load("domus/domus_funcs.txt")
		self.p.loadlabels("domus/domus_page_zero.txt")
		

	def finish_ins(self, ins):
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


	def zonedesc(self, p, adr, priv = None):
		self.do_desc(adr, 0, "Zone", ZoneDesc)
		x = p.m.rd(adr + 17)
		if x != 0:
			p.todo(x, self.sharedesc)

	def sharedesc(self, p, adr, priv = None):
		self.do_desc(adr, 8, "Share", ShareDesc)

	def progdesc(self, p, adr, priv = None):
		# 1B0 = has procdesc
		# 1B1 = reentrant
		# 1B5 = params
		# 1B6 = paged
		# 1B7 = reserve
		# 1B15 = ??
		p.a['progdesc'] = adr
		self.do_desc(adr, 0, "Program", ProgDesc)

	def procdesc(self, adr, priv = None):
		p = self.p
		self.p.a['procdesc'] = adr
		self.do_desc(adr, p.m.rd(adr + 3), "Process", ProcDesc)

		self.msgdesc(p, p.m.rd(adr + 9))

		self.progdesc(p, p.m.rd(adr + 10))

		# Try the PSW
		self.disass(p.m.rd(adr + 19)>>1)

		# Try the CLEAR_INTERRUPT
		try:
			cli = p.m.rd(adr + 26)
			print("CLI " + p.m.afmt(cli))
			if cli != 0:
				self.disass(cli)
		except:
			pass

	def msgdesc(self, p, adr, priv = None):
		if adr == 0 or adr == None:
			return
		if self.do_desc(adr, 10, "Message", MsgDesc):
			try:
				x = p.m.rd(adr + 2)
			except:
				return
			if x != 0:
				p.todo(p.m.rd(adr + 2), self.msgdesc)

	def pagedesc(self, p, adr, priv = None):
		p.a['pagedesc'] = adr
		self.do_desc(adr, 0, "Paging", PageDesc)

		w = p.m.rd(adr + 3)
		i = p.m.rd(w)
		self.do_desc(w, i + 1, "Page_Table", (
			( 1, 		"n_pages" ),
			( i,		"pageentries"),
		))

		w = p.m.rd(adr + 4)
		i = p.m.rd(w)
		self.do_desc(w, i + 1, "Page_Map", (
			( 1,		"n_pages" ),
			( i,		"pageentries"),
		))

		w = p.m.rd(adr + 5)
		if w != 0:
			p.setlabel(w, "Paging_Statproc")
			self.disass(w)

	def do_desc(self, a, l, n, desc):
		p = self.p
		dtype = n + "Descriptor"
		try:
			x = p.t.find(a, dtype)
			if x != None:
				return False
		except:
			pass

		if l == 0:
			for i in desc:
				try:
					p.m.rd(a + l)
				except:
					break
				l += i[0]
		x = p.t.add(a, a + l, dtype)
		x.blockcmt += n + " descriptor\n"
		x.fill = False
		i = 0
		for j in desc:
			if j[1] == "name":
				x = dot_txt(p, a+i, a + i + j[0])
			else:
				x = word(p, a + i)
			x.cmt.append("+%d " % i + j[1])
			i += j[0]
			if i >= l:
				break
		while i < l:
			x = word(p, a + i)
			x.cmt.append("+%d" % i)
			i += 1
		return True
