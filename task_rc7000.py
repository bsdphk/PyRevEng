#!/usr/local/bin/python
#

from __future__ import print_function

import sys

import pyreveng

import domus.cpu
import domus.mem
import domus.inter
import domus.reloc_file
import domus.const as const
import domus.desc as desc

import render
import topology

dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/rc7000/"
dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/FILES/"

class DomusError(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)

def dofile(filename, obj = None, skip = 0):

	print("DOFILE", filename, obj);

	try:
		import os
		fn = filename
		load_file = domus.reloc_file.reloc_file(fn, skip)
		filename=os.path.basename(fn)
	except:
		fn = dn + filename
		load_file = domus.reloc_file.reloc_file(fn, skip)

	objidx = load_file.build_index()
	print(objidx)
	for obj in objidx:

		print("tfm",
		    "%04x" % skip,
		    "%04x" % (skip + objidx[obj][0]*2),
		    "%04x" % (skip + objidx[obj][1]*2),
		    objidx[obj])

		p = pyreveng.pyreveng(domus.mem.mem_domus())
		cpu = domus.cpu.cpu(p)

		cpu.iodev[9] = "TTYOUT"

		load_file.load(p.m, obj, silent=True)

		ld = load_file.rec_end
		print(obj, ld)

		if ld == None and len(objidx) != 1:
			ld = load_file.min_nrel
			p.todo(ld, cpu.disass)
		elif ld == None:
			pass
		elif ld == 0x8000:
			pass
		else:
			desc.procdesc(p, ld, cpu.disass)

		for i in range(0,256):
			try:
				q = p.m.rdqual(i)
				d = p.m.rd(i)
			except:
				continue
			if q > 0:
				cpu.disass(d)
			continue
			j = 0o006200 | i
			if j in cpu.special:
				p.setlabel(d, cpu.special[j][0])
				x = p.t.add(i, i + 1, "PZ_CALL")
				x.render = ".WORD   %o%s" % (d, p.m.qfmt(q))
				x.blockcmt += "\n"
				x.cmt.append(cpu.special[j][0])
				if len(cpu.special[j]) > 1:
					for k in cpu.special[j][1]:
						x.cmt.append(k)

		if filename == "__.MUC":
			p.todo(0o100017, cpu.disass)
			p.todo(0o100034, cpu.disass)

		if filename == "__.INT":

			tbl_base = 0o100015
			def xx(n):
				i  = n + tbl_base
				if n in domus.inter.intins:
					x = domus.inter.intins[n]
					y = const.word(p,i)
					y.cmt.append(str(x))
					a = p.m.rd(i)
					if len(x) == 2:
						p.setlabel(a, x[1] + " **********")
					else:
						p.setlabel(a, x[1])
				x = p.m.rd(i)
				if x != 0:
					p.todo(x, cpu.disass)

			for i in domus.inter.intins:
				xx(i)

		if filename == "__.DOMUS":
			# DOMUS
			p.todo(0x11f1, cpu.disass)
			p.t.a['page_base'] = 0x137a
			desc.pagedesc(p, 0x1007)
			for pg in range(3,20):
				aa = 0x137a + pg * 0x100
				x = p.t.add(aa, aa + 1, "page %d" % pg)
				x.a['cmt'] = "; PAGE %d" % pg
			for c in range(0,19):
				aa = 0x1d90 + 5 * c
				const.word(p, aa)
				const.dot_txt(p, aa + 1, aa + 4)
				const.word(p, aa + 4)
				nw = p.m.rd(aa)
				da = (nw & 0x7fff) + p.t.a['page_base']
				p.todo(da, cpu.disass)
				print("CMD: %x -> %x" % (aa,da))

		if filename == "__.MUSIL":
			#p.todo(0o20550, cpu.disass)
			#p.todo(0o14341, cpu.disass)
			desc.zonedesc(p, 0o11634)
			x = p.t.add(0o012461, 0o012474, "Func")
			x = p.t.add(0o012474, 0o012477, "Func")
			x = p.t.add(0o012477, 0o012512, "Func")
			x = p.t.add(0o013272, 0o013303, "Func")

			const.dot_txt(p, 0o012517, None)

			def do_list(p,a, nw):
				while True:
					x = p.t.add(a - 4, a + nw, "XXXTBL")
					const.dot_txt(p, a - 4, a)
					for i in range(0,nw):
						const.word(p, a + i, "%o")
					n = p.m.rd(a)
					if n == 0:
						break
					a = n

			do_list(p, 0o016451, 2)
			do_list(p, 0o026100, 4)
			do_list(p, 0o026270, 4)

			for a in range(0o015673, 0o015706):
				p.todo(p.m.rd(a), cpu.disass)
				

			a = 0o12526
			while True:
				x = p.t.add(a, a + 5, "XXXTBL")
				const.dot_txt(p, a + 2, a + 5)
				p.todo(p.m.rd(a + 1), cpu.disass)
				const.word(p, a, "%o")
				const.word(p, a + 1, "%o")
				n = p.m.rd(a)
				if n == 0:
					break;
				a = n + 2

			# calls to 20574'
			p.todo(0o20716, cpu.disass)
			p.todo(0o14600, cpu.disass)

			p.todo(0o17343, cpu.disass)

			p.todo(0o17341, cpu.disass)
			p.todo(0o015271, cpu.disass)

		p.run()

		if filename == "__.CATW":
			# See RCSL 43-GL-7915 p35
			pgd = p.a['progdesc']
			print("CATW", pgd)
			x = const.word(p, pgd + 7)
			x.cmt.append(" +7 First Area Process")
			x = const.word(p, pgd + 8)
			x.cmt.append(" +8 Top Area Process")
			x = const.word(p, pgd + 9)
			x.cmt.append(" +9 Head of Unit Chain")
			x = const.word(p, pgd + 10)
			x.cmt.append(" +10 Chain of Head of Unit Chain")
			a = pgd + 11
			while True:
				x = p.t.add(a, a + 20, "UnitDesc")

				x = const.word(p, a)
				x.cmt.append(" +0 Driver name reference")

				x = const.word(p, a + 1)
				x.cmt.append(" +1 Unit number")

				x = const.word(p, a + 2)
				x.cmt.append(" +2 chain")

				x = const.word(p, a + 3)
				x.cmt.append(" +3 size of unit desc")

				x = const.dot_txt(p, a + 4, a + 7)
				x = const.dot_txt(p, a + 7, a + 10)

				x = const.word(p, a + 10)
				x.cmt.append(" +10 Kit displacement")
				x = const.word(p, a + 11)
				x.cmt.append(" +11 Kit displacement")

				n = p.m.rd(a + 2)
				if n == 0:
					break
				a = n

		p.run()

		cpu.to_tree()

		ff = topology.topology(p)
		ff.build_bb()
		ff.segment()
		ff.dump_dot(digraph='size="7.00, 10.80"\nconcentrate=true\ncenter=true\n')


		r = render.render(p)
		r.add_flows()

		if obj != None:
			fn = "/tmp/" + filename + "_" + obj
		else:
			fn = "/tmp/" + filename
		print("---------->", fn)
		r.render(fn)
		sys.stdout.flush()

if __name__ == "__main__":

	if False:
		import os 

		fl = os.listdir(dn)
		for i in fl:
			try:
				dofile(i)
				sys.stdout.flush()
			except:
				pass
	else:
		#dofile("__.CODEP", "P0261")
		#dofile("__.INT")
		#dofile("__.PTR", skip = 1)
		#dofile("__.MUM")
		#dofile("__.CHECK")
		#dofile("__.CATW")
		dofile("__.CATLI")
		#dofile("__.FSLIB")
		#for o in (0x55c, 0x4b11, 0x8742):
		#	dofile("/home/phk/rc7000_atm_asnaes.bin", None, o)
		#pass
