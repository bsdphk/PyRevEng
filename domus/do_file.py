#!/usr/local/bin/python
#

#----------------------------------------------------------------------
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#----------------------------------------------------------------------
import os

import pyreveng

import domus.cpu
import domus.mem
import domus.inter
import domus.reloc_file
import domus.const as const
import domus.desc as desc

import render
import topology

#---------------------------------------------------------------------------
# Try to locate an executable file

filedirs = (
	"",
	"/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/",
	"/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/rc7000/",
	"/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/FILES/",
)

def find_file(filename, skip = 0):
	for d in filedirs:
		try:
			load_file = domus.reloc_file.reloc_file(
			    d + filename,
			    skip
			)
			no = load_file.build_index()
			assert len(no) != 0
			print("Loaded file: " + filename)
			if d != "":
				print("From: " + d)
			s = os.path.basename(d + filename)
			if s[:3] == "__.":
				s = s[3:]
			print("Basename: " + s)
			print()
			load_file.basename = s
			if len(no) > 1:
				print(
				    "This is library file "
				    "with %d objects" % len(no)
				)
				load_file.library = True
			else:
				load_file.library = False
			return load_file
		except:
			pass
	return None

#---------------------------------------------------------------------------

def load_obj(load_file, obj):

	p = pyreveng.pyreveng(domus.mem.mem_domus())
	cpu = domus.cpu.cpu(p)
	load_file.load(p.m, obj, silent=True)
	ld = load_file.rec_end
	p.a['library'] = load_file.library
	p.a['objname'] = obj
	p.a['basename'] = load_file.basename
	p.a['entrypoint'] = ld
	if obj == None:
		print("Loaded object from: " + load_file.basename)
	else:
		print("Loaded " + obj + " from: " + load_file.basename)
	print()
	return p

#---------------------------------------------------------------------------

def pz_entry(p, cpu):
	# XXX: does not work right now
	return
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


#---------------------------------------------------------------------------

def auto_magic(p):
	cpu = p.c["domus"]
	ld = p.a['entrypoint']
	if ld == None:
		pass
	elif ld == 0x8000:
		pass
	elif p.a['library'] == True:
		cpu.disass(ld)
	else:
		desc.procdesc(p, ld, cpu.disass)
	p.run()

#---------------------------------------------------------------------------

def auto_hints(p):
	id = p.a['basename']
	objname = p.a['objname']
	if objname != None:
		id += "_" + objname
	try:
		exec("import domus.hints." + id + " as hint\nhint.hint(p)")
		print("Hints loaded from domus.hints.%s" % id)
		p.run()
	except ImportError:
		print("No auto hints found (domus.hints.%s)" % id)
	print()

#---------------------------------------------------------------------------

def finish(p):

	p.run()
	
	for i in p.c:
		p.c[i].to_tree()

	ff = topology.topology(p)
	ff.build_bb()
	ff.segment()
	ff.dump_dot(
	    digraph='size="7.00, 10.80"\nconcentrate=true\ncenter=true\n'
	)

	r = render.render(p)
	r.add_flows()

	if p.a['objname'] != None:
		fn = "/tmp/_." + p.a['basename'] + "_" + p.a['objname']
	else:
		fn = "/tmp/_." + p.a['basename']
	fn += ".txt"
	print("Output written to:", fn)
	r.render(fn)
