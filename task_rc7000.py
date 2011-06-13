#!/usr/local/bin/python
#

from __future__ import print_function

import mem
import array

import tree
import pyreveng

import cpu_domus
import mem_domus
import cpu_domus_int
import file_domus

class DomusError(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)

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
	

if __name__ == "__main__" and False:
	import os

	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
	fl = os.listdir(dn)
	for i in fl:
		try:
			df = file_domus.file_domus(dn + i)
			if len(df.index) > 1:
				print(len(df.index), i)
		except:
			pass
  
	exit (0)





def dofile(filename, obj = None):

	print("DOFILE", filename, obj);
	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/FILES/"
	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
	fn = dn + filename

	p = pyreveng.pyreveng(mem_domus.mem_domus())
	p.cpu = cpu_domus.domus()
	p.t.recurse()

	p.cpu.iodev[9] = "TTYOUT"

	p.load_file = file_domus.file_domus(fn)
	if False:
		print("OBJS:", p.load_file.index)
		p.load_file.load(p.m, "TESTM")
	else:
		p.load_file.load(p.m, obj)
	ld = p.load_file.rec_end
	if obj != None:
		pass
	elif ld == None:
		pass
	elif ld == 0x8000:
		pass
	else:
		p.todo(p.load_file.rec_end, p.cpu.procdesc)

	for i in range(0,256):
		try:
			q = p.m.rdqual(i)
			if q > 0:
				p.todo(p.m.rd(i), p.cpu.disass)
		except:
			pass

	if filename == "__.INT":

		tbl_base = 0o100015
		def xx(n):
			i  = n + tbl_base
			if n in cpu_domus_int.intins:
				x = cpu_domus_int.intins[n]
				y = cpu_domus.word(p,i)
				y.cmt.append(str(x))
				a = p.m.rd(i)
				if len(x) == 2:
					p.setlabel(a, x[1] + " **********")
				else:
					p.setlabel(a, x[1])
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

	if fn == dn + "__.CODEP":
		p.todo(0o10000, p.cpu.disass)
		pass

	if fn == dn + "__.CDFP1":
		p.todo(0o10000, p.cpu.disass)

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

	if fn == dn + "__.MUSIL":
		#p.todo(0o20550, p.cpu.disass)
		#p.todo(0o14341, p.cpu.disass)
		p.cpu.zonedesc(p, 0o11634)
		x = p.t.add(0o012461, 0o012474, "Func")
		x = p.t.add(0o012474, 0o012477, "Func")
		x = p.t.add(0o012477, 0o012512, "Func")
		x = p.t.add(0o013272, 0o013303, "Func")

		cpu_domus.dot_txt(p, 0o012517, None)

		def do_list(p,a, nw):
			while True:
				x = p.t.add(a - 4, a + nw, "XXXTBL")
				cpu_domus.dot_txt(p, a - 4, a)
				for i in range(0,nw):
					cpu_domus.word(p, a + i, "%o")
				n = p.m.rd(a)
				if n == 0:
					break
				a = n

		do_list(p, 0o016451, 2)
		do_list(p, 0o026100, 4)
		do_list(p, 0o026270, 4)

		for a in range(0o015673, 0o015706):
			p.todo(p.m.rd(a), p.cpu.disass)
			

		a = 0o12526
		while True:
			x = p.t.add(a, a + 5, "XXXTBL")
			cpu_domus.dot_txt(p, a + 2, a + 5)
			p.todo(p.m.rd(a + 1), p.cpu.disass)
			cpu_domus.word(p, a, "%o")
			cpu_domus.word(p, a + 1, "%o")
			n = p.m.rd(a)
			if n == 0:
				break;
			a = n + 2

		# calls to 20574'
		p.todo(0o20716, p.cpu.disass)
		p.todo(0o14600, p.cpu.disass)

		p.todo(0o17343, p.cpu.disass)

		p.todo(0o17341, p.cpu.disass)
		p.todo(0o015271, p.cpu.disass)

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
	if obj != None:
		p.render("/tmp/" + filename + "_" + obj)
	else:
		p.render("/tmp/" + filename)
	#p.t.recurse()

if __name__ == "__main__":

	if False:
		import os 

		dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
		fl = os.listdir(dn)
		for i in fl:
			try:
				dofile(i)
			except:
				pass
	else:
		#dofile("__.CODEP", "P0261")
		dofile("__.MUSIL")
		#dofile("__.CATLI")
