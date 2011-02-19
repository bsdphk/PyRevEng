#!/usr/local/bin/python
#

from __future__ import print_function

import mem
import array

import tree
import pyreveng

import cpu_domus

class DomusError(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)

def radix40(y):
	s = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.?"
	v1 = y[0]
	v2 = y[1]
	l3 = v1 % 40
	l2 = (v1 / 40) % 40
	l1 = (v1 / (40*40)) % 40
	l5 = (v2 / 32) % 40
	l4 = (v2 / (40 * 32)) % 40
	#print(len(s), l1, l2, l3, l4, l5, s[l1], s[l2], s[l3], s[l4], s[l5])
	return ((s[l1] + s[l2] + s[l3] + s[l4] + s[l5]).strip(), v2 & 0x1f)

def domus_load(p, fn, off=0x1000, offhi=0x8000, member=None):
	dotend = None
	skip = False

	f = open(fn, "rb")
	b = f.read()
	f.close()
	mf = array.array("H", b)

	if member != None:
		skip = True

	a = 0
	while a < len(mf):
		t = mf[a]
		if t == 0:
			a += 1
			continue
		if t >= 0x10:
			print("Illegal record type %d at 0x%x" % (t, a))
			return None
		l = mf[a + 1]
		b = 0
		s = ""
		y = list()
		r = ""
		c = 0
		for i in range(l, 65536 + 6):
			x = mf[a + b]
			c += x
			if b == 0:
				s += "%d" % x
			elif b == 1:
				s += " %3d" % (x - 65536)
			elif b < 5:
				r += "%05o" % (x / 2)
				s += " %06o" % (x/2)
				if x & 1:
					s += '*'
			else:
				s += " %04x" % x
			if b > 5:
				y.append(x)
			b += 1
		c &= 0xffff
		assert c == 0
		if not skip:
			print(s)

		for j in range(0,len(y)):
			q = int(r[j])
			if q == 0:
				pass
			elif q == 1:
				pass
			elif q == 2:
				y[j] += off
			elif q == 3:
				y[j] += off * 2
			elif q == 7:
				y[j] += offhi
			else:
				print("RELOC %s ???" % r[j])

		if t == 9:
			if not skip:
				print ("  .HIMEM", y)
		elif t == 7:
			x = radix40(y)
			if x[0] == member:
				skip = False
			if not skip:
				print ("  .TITL %s" % x[0])
		elif t == 6:
			if not skip:
				print ("  .END 0x%0x" % y[0])
				dotend = y[0]
			if member != None and not skip:
				break
		elif t == 2:
			ax = y[0]
			y = y[1:]
			for j in range(0,len(y)):
				p.m.setflags(ax + j, None, p.m.can_read|p.m.can_write,p.m.invalid)
				p.m.wr(ax + j, y[j] & 0xffff)
				p.m.wrqual(ax + j, int(r[j + 1]))
		else:
			print(r)
			print(y)
			break
		a += b
	return dotend

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
	x = p.t.add(a, a + l, "descriptor")
	x.blockcmt += n + "descriptor\n"
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

def progdesc(p, a, priv = None):
	do_desc(p, a, 7, "Program", (
		( 1, "spec"),
		( 1, "start"),
		( 1, "chain"),
		( 1, "size"),
		( 3, "name"),
	))

def procdesc(p, a, priv = None):
	do_desc(p, a, p.m.rd(a + 3), "Process", (
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
	))
	p.todo(p.m.rd(a + 19)/2, p.cpu.disass)
	progdesc(p, p.m.rd(a + 10))

class mem_domus(mem.base_mem):
	def __init__(self, start = 0, end = 0x10000):
		mem.base_mem.__init__(self, start, end, 16, 3, True)
		self.qchar= ("0", " ", "'", '"', 'a', 'b', 'c', '*')

	def afmt(self, a):
		if a < 0x1000:
			return "%04x " % a
		elif a < 0x8000:
			return "%04x'" % a
		else:
			return "%04x*" % a

	def qfmt(self, q):
		return self.qchar[q]

if __name__ == "__main__":

	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/FILES/"
	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
	fn = dn + "__.DOMAC"
	fn = dn + "__.MUI"
	fn = dn + "__.MUC"
	fn = dn + "__.LIBE"
	fn = dn + "__.FSLIB"
	fn = dn + "__.ULIB"
	fn = dn + "__.INT"
	fn = dn + "__.DKP"
	fn = dn + "__.TT009"
	fn = dn + "__.MUM"
	fn = dn + "__.CATIX"
	fn = dn + "__.CAP2"
	fn = dn + "__.CATLI"
	fn = dn + "__.DOMUS"
	fn = dn + "__.PTP"

	p = pyreveng.pyreveng(mem_domus())
	p.cpu = cpu_domus.domus()
	p.t.recurse()

	#domus_load(m, fn, member="P0155")
	l = domus_load(p, fn)
	if l < 0x8000:
		p.todo(l, procdesc)

	if False:
		# DOMUS
		p.t.a['page_base'] = 0x137a
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
	p.render()
	p.t.recurse()
