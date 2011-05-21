#!/usr/local/bin/python
#

from __future__ import print_function

import mem
import array

import tree
import pyreveng

import cpu_domus
import cpu_domus_int
import file_domus

class DomusError(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)

class word(tree.tree):
	def __init__(self, p, adr, fmt = "%d"):
		tree.tree.__init__(self, adr, adr + 1, "word")
		p.t.add(adr, adr + 1, "word", True, self)
		self.fmt = fmt
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
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
		tree.tree.__init__(self, start, end, "dot_txt")
		p.t.add(start, end, "dot_txt", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t, lvl):
		s = ".TXT\t'"
		for i in range(t.start, t.end):
			q = p.m.rdqual(i)
			if q != 1:
				raise DomusError(t.start, ".TXT is relocated")
			x = p.m.rd(i)
			s += mem.ascii(x >> 8)
			s += mem.ascii(x)
		s += "'"
		return (s,)

def do_desc(p, a, l, n, desc):
	if l == 0:
		for i in desc:
			try:
				p.m.rd(a + l)
			except:
				break
			l += i[0]
	x = p.t.add(a, a + l, n + "Descriptor")
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

def paging(p, a, priv = None):
	do_desc(p, a, 0, "RCSL-43-RI-0142 Paging", (
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
	))

	w = p.m.rd(a + 3)
	do_desc(p, w, 0, "Page Table", (
		( 1, "n_pages" ),
		( p.m.rd(w), "pageentries"),
	))

	w = p.m.rd(a + 4)
	do_desc(p, w, 0, "Page Map", (
		( 1, "n_pages" ),
		( p.m.rd(w), "pageentries"),
	))

	w = p.m.rd(a + 5)
	if w != 0:
		p.setlabel(w, "Paging_Statproc")
		p.todo(w, p.cpu.disass)
	

class mem_domus(mem.base_mem):
	def __init__(self, start = 0, end = 0x10000):
		mem.base_mem.__init__(self, start, end, 16, 3, True)
		self.qchar= ("0", " ", "'", '"', 'a', 'b', 'c', '*')
		self.dpct = "%06o"

	def afmt(self, a):
		if a < 0x1000:
			return "%06o " % a
		elif a < 0x8000:
			return "%06o'" % a
		else:
			return "%06o*" % a

	def qfmt(self, q):
		return self.qchar[q]

if __name__ == "__main__":

	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/FILES/"
	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
	fn = dn + "__.DOMAC"
	fn = dn + "__.MUC"
	fn = dn + "__.LIBE"
	fn = dn + "__.TT009"
	fn = dn + "__.CATIX"
	fn = dn + "__.MUI"
	fn = dn + "__.INT"
	fn = dn + "__.CAP2"
	fn = dn + "__.DOMUS"
	fn = dn + "__.DKP"
	fn = dn + "__.ULIB"
	fn = dn + "__.FSLIB"
	fn = dn + "__.PTP"
	fn = dn + "__.ULIB"
	fn = dn + "__.INT"
	fn = dn + "__.CATLI"

	p = pyreveng.pyreveng(mem_domus())
	p.cpu = cpu_domus.domus()
	p.t.recurse()

	p.cpu.iodev[9] = "TTYOUT"

	p.load_file = file_domus.file_domus(fn)
	if False:
		print("OBJS:", p.load_file.index)
		p.load_file.load(p.m, "TESTM")
	else:
		p.load_file.load(p.m)
	ld = p.load_file.rec_end
	if ld == None:
		pass
	elif ld == 0x8000:
		pass
	else:
		p.todo(p.load_file.rec_end, p.cpu.procdesc)

	if fn == dn + "__.INT":

		for i in range(0,256):
			try:
				q = p.m.rdqual(i)
				if q > 0:
					p.todo(p.m.rd(i), p.cpu.disass)
			except:
				pass
		tbl_base = 0o100015
		def xx(n):
			i  = n + tbl_base
			if n in cpu_domus_int.intins:
				x = cpu_domus_int.intins[n]
				y = word(p,i)
				y.cmt.append(str(x))
				a = p.m.rd(i)
				if len(x) == 1:
					p.setlabel(a, x[0] + " **********")
				else:
					p.setlabel(a, x[0])
			x = p.m.rd(i)
			if x != 0:
				p.todo(x, p.cpu.disass)

		for i in cpu_domus_int.intins:
			xx(i)
		

	if fn == dn + "__.MUM":
		# MUM
		for i in range(0,256):
			try:
				q = p.m.rdqual(i)
				if q != 1:
					p.todo(p.m.rd(i), p.cpu.disass)
			except:
				continue

	if fn == dn + "__.DKP":
		p.todo(0o100000, p.cpu.disass)

	if fn == dn + "__.CATLI":
		dx = dict()
		p.a['musil_code'] =  dx
		dx[1] = ("GETPARAMS", "A", "A", "A", "A", "V", "N")
		dx[2] = ("?", "A", "V", "A", "A", "N")
		dx[3] = ("?", "A", "N")
		dx[4] = ("?", "A", "N")
		dx[5] = ("?", "A", "N")
		dx[6] = ("?", "A", "A", "A", "N")
		dx[7] = ("?", "A", "V", "A", "A", "N")
		dx[8] = ("exit", "V",)

	if fn == dn + "__.PTP":
		pass

	if fn == dn + "__.DOMUS":
		# DOMUS
		p.todo(0x11f1, p.cpu.disass)
		p.t.a['page_base'] = 0x137a
		paging(p, 0x1007)
		for pg in range(3,20):
			aa = 0x137a + pg * 0x100
			x = p.t.add(aa, aa + 1, "page %d" % pg)
			x.a['cmt'] = "; PAGE %d" % pg
		for c in range(0,19):
			aa = 0x1d90 + 5 * c
			word(p,aa)
			dot_txt(p, aa + 1, aa + 4)
			word(p,aa + 4)
			nw = p.m.rd(aa)
			da = (nw & 0x7fff) + p.t.a['page_base']
			p.todo(da, p.cpu.disass)
			print("CMD: %x -> %x" % (aa,da))

	p.run()

	if False:
		for g in p.t.gaps():
			for i in range(g[0],g[1]):
				if p.m.tstflags(i, None, p.m.invalid):
					continue
				q = p.m.rdqual(i)
				x = p.m.rd(i)
				if q == 1 and False:
					p.cpu.disass(p, i)
				else:
					p.t.add(i, i + 1, "gap")
	print("----------")
	p.render("/tmp/_domus")
	#p.t.recurse()
