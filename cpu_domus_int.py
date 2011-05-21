#!/usr/local/bin/python
#

from __future__ import print_function

import mem_domus
import file_domus

dn = "/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"

libx= ( "CODEP", "CODEX", "ULIB", "FSLIB",)

codeprocs = {
"CODEP::P0084": ("FINIS", "V",),
"CODEP::GETER": ("GETER", "A", "V", "A", "A", "N"),
"CODEP::P0085": ("P0085", "A", "A", "A", "N"),
"CODEP::P0086": ("P0086", "A", "V", "A", "N"),
"CODEP::P0150": ("P0150", "A", "N"),
"CODEP::P0154": ("P0154", "A", "A", "N"),
"CODEP::P0159": ("P0150", "A", "A", "N"),
"CODEP::P0260": ("GETPARAMS", "A", "A", "A", "A", "V", "N"),
#CODEP::P0261": ("CONNECTFILE", ...RCSL-43-GL-10639
#CODEP::P0262": ("SPLITSHARE", ...RCSL-43-GL-10639
"CODEP::P0263": ("GETNAME", "A", "A", "A", "N"),
#CODEP::P0264": ("GETERROR", ...RCSL-43-GL-10639
"CODEP::PYY86":	("PYY86", "A", "V", "A", "A", "N"),
"CODEP::P0XXX":	("P0XXX", "A", "N"),
}

def ident_lib_module(p, adr):
	print("Try to identify CODE routine at %o" % adr)
	for ll in libx:
		df = file_domus.file_domus(dn + "__." + ll)
		for i in df.index:
			mx = mem_domus.mem_domus()
			df.load(mx, i, silent=True)
			oo = 0o10000
			match = 0
			skip = 0
			target = df.max_nrel + 1 - oo
			for ax in range(0, target):
				try:
					q = mx.rdqual(ax + oo)
					dx = mx.rd(ax + oo)
				except:
					target -= 1
					#print("REFRD %o" % ax)
					continue
				if q != 1:
					#print("REFQ %o" % ax, q)
					skip += 1
					continue
				try:
					dy = p.m.rd(adr + ax)
				except:
					#print("CODRD %o" % ax)
					continue
				if dx == dy:
					match += 1
			if match + skip != target:
				continue
			print("Code Routine at %o matches %s::%s  (" % (adr, ll, i), match, skip, df.load_words, ")")
			idx = ll + "::" + i
			x = p.t.add(adr, adr + df.max_nrel - oo, "CodeProc")
			x.blockcmt += "CODE PROCEDURE " + i + " FROM " + ll + "\n"
			p.setlabel(adr, i)
			if idx in codeprocs:
				return codeprocs[idx]
			return None

intins = {

0:	( "STOP", ),
1:	( "ANDD", "ARG", "N"),
2:	( "LOADD", "ARG", "N"),
3:	( "+D", "ARG", "N"),
4:	( "-D", "ARG", "N"),
5:	( "SHIFTD", "ARG", "N"),
6:	( "EXTRACTC", "ARG", "N"),
7:	( "*D", "ARG", "N"),
8:	( "/D",),
9:	( "ANDC", "CONST", "N"),
10:	( "LOADC", "CONST", "N"),
11:	( "+C", "CONST", "N"),
12:	( "-C", "CONST", "N"),
13:	( "SHIFTC", "CONST", "N"),
14:	( "EXTRACTC", ),
15:	( "*C", "CONST", "N"),
16:	( "/C", "CONST", "N"),
17:	( "AND", "ADDR", "N"),
18:	( "LOAD", "ADDR", "N"),
19:	( "+", "ADDR", "N"),
20:	( "-", "ADDR", "N"),
21:	( "SHIFT", "ADDR", "N"),
22:	( "EXTRACT",),
23:	( "*", "ADDR", "N"),
24:	( "/", "ADDR", "N"),
25:	( "LOAD_NEGATIVE", ),
26:	( "LOAD_BYTE", "A", "N"),
27:	( "LOAD_BYTEWORD", "A", "N"),
28:	( "JUMP", "JUMP", "N"),
29:	( "LINK",),
30:	( "MOVEWORD", ">>2", "ADDR", "V", "N"),
31:	( "MOVESTRING", "A", "A", "V", "N"),
32:	( "??COMPAREWORD",),
33:	( "COMPARESTRING", "A", "A", "V", "N"),
34:	( "STORE_REGSITER", "ADDR", "N"),
35:	( "TRANSLATE", "A", "A", "A", "N"),
36:	( "CONVERT", "A", "A", "A", "V", "N"),
37:	( "OPMESS", "A", "N"),
38:	( "OPIN", "A", "N"),
39:	( "OPWAIT", "ADDR", "N"),
40:	( "CALL",),
41:	( "OPTEST",),
42:	( "MOVE", "BITS", "A", "V", "A", "V", "V", "N"),
43:	( "OPSTATUS",),
44:	( "BINDEC", "V", "A", "N"),
45:	( "DECBIN", "A", "ADDR", "N"),
46:	( "CHAR", "V", "A", "V", "N"),
47:	( "GOTO", ),
48:	( "GO_CODE", "GC" ),

49:	( "OP49", "V", "N"),
50:	( "OP50", ),
51:	( "OP51", "I", ),
52:	( "OP52", ),
53:	( "OP53", ),
54:	( "OP54", ),
55:	( "OP55", "I", "N"),
56:	( "OP56", "A", "V", "N"),
57:	( "OP57", "A", "V", "N"),

128:	( "GETREC", "ZONE", "ADDR", "N"),
129:	( "PUTREC", ">>2", "ADDR", "V", "N"),
130:	( "WAITTRANSFER", "ZONE", "N"),
131:	( "REPEATSHARE", "ZONE", "N"),
132:	( "TRANSFER", "ZONE", ),
133:	( "INBLOCK", "ZONE", "N"),
134:	( "OUTBLOCK", "ZONE"),
135:	( "FREESHARE", "ZONE", "ADDR", "N"),
136:	( "INCHAR", "ZONE", ),
137:	( "OUTSPACE", "ZONE", ),
138:	( "OUTCHAR", ">>2", "ADDR", "V", "N"),
139:	( "OUTNL", ),
140:	( "OUTEND", ),
141:	( "OUTTEXT",	"ZONE", "V", "N"),
142:	( "OUTOCTAL",),
143:	( "SETPOS",	"ZONE", "V", "V", "N"),
144:	( "CLOSE",	"ZONE", "V", "N"),
145:	( "OPEN",	"ZONE", "V", "N"),
146:	( "WAITZONE",	">>2", "ADDR", "N"),

218:	( "NEWCAT",	">>2", "A", "V", "N"),
219:	( "FREECAT",	">>2", "A", "N"),

230:	( "CREATEENTRY", "ZONE", "V", "V", "N"),
231:	( "LOOKUPENTRY", ">>2", "ADDR", "A", "N"),
232:	( "CHANGEENTRY", ),
233:	( "REMOVEENTRY", ">>2", "ADDR", "N"),
234:	( "INITCATALOG", "ZONE", "V", "V", "N"),
235:	( "SETENTRY", ),
}

def disass(p, adr, priv = None):

	#print("INT %o" % adr)
	try:
		x = p.t.find(adr, "domus_int")
		if x != None:
			return
	except:
		pass

	q = p.m.rdqual(adr)
	if q != 1:
		print("INT adr %o qualifier %d" % (adr, q))
		return

	iw = p.m.rd(adr)
	ea = adr + 1
	op = iw >> 8
	arg = iw & 0xff
	if not op in intins:
		print("INT adr %6o iw %6o op %3d arg %3d UNKNOWN" % (adr, iw, op, arg))
		return
	l = intins[op]
	#print("INT adr %o iw %o op %d arg %d:" % (adr, iw, op, arg), l)
	s = l[0] + "("
	x = ""
	j = 1
	while j < len(l):
		i = l[j]
		j += 1
		t = None
		if i == ">>2":
			arg >>= 2
		elif i == "BITS":
			arg = p.m.rd(ea)
			ea += 1
		elif i == "I":
			tgt = p.m.rd(ea)
			t = ">%o" % tgt
			ea += 1
			p.todo(tgt, p.cpu.disass)
		elif i == "ARG":
			t = "%o" % arg
		elif i == "JUMP":
			tgt = p.m.rd(ea)
			t = "CC=%o, %o" % (arg, tgt)
			p.todo(tgt, disass)
			ea += 1
		elif i == "CONST":
			t = "%o" % p.m.rd(ea)
			ea += 1
		elif i == "ZONE":
			t = "zone=%o" % p.m.rd(ea)
			za = p.m.rd(ea)
			p.todo(za, p.cpu.zonedesc)
			za = p.m.rd(za + 3)
			p.todo(za, p.cpu.disass)
			arg >>= 2
			ea += 1
		elif i == "ADDR":
			t = "%o" % p.m.rd(ea)
			ea += 1
		elif i == "A":
			tq = p.m.rdqual(ea)
			tgt = p.m.rd(ea)
			ea += 1
			if tq == 3:
				ax = "%o'*2" % (tgt >> 1)
				if tgt & 1:
					ax += "+1"
			else:
				ax = "%o" % tgt + p.m.qfmt(tq)
			if arg & 3 == 0:
				t = "A0: int=" + ax
			elif arg & 3 == 1:
				t = "A1: string=" + ax
			elif arg & 3 == 2:
				t = "A2: file=" + ax
			else:
				t = "A2: zone=" + ax
			arg >>= 2
		elif i == "V":
			if arg & 3 == 0:
				t = "V0: %o" % p.m.rd(ea)
				ea += 1
			elif arg & 3 == 1:
				t = "V1: R"
			elif arg & 3 == 2:
				t = "V2: (%o)" % p.m.rd(ea)
				ea += 1
			else:
				t = "V3: R"
			arg >>= 2
		elif i == "GC":
			if not 'musil_code' in p.a:
				p.a['musil_code'] = dict()
			y = p.a['musil_code']

			pd = p.a['procdesc']
			ta = p.m.rd(pd - arg)


			t = "[%d]=%o" % (-arg, ta)
			t += ", %o" % p.m.rd(ea)
			ea += 1
			p.todo(ta, p.cpu.disass)
			if not arg in y:
				xx = ident_lib_module(p, ta)
				if xx != None:
					y[arg] = xx
			if arg in y:
				t += ", " + y[arg][0]
				l += y[arg][1:]
			else:
				print("INT adr %o CODE %d unknown" % (adr, arg))
		elif i == "N":
			p.todo(ea, disass)
		else:
			print("???", i)
			break

		if t != None:
			s += x
			s += t
			x = ", "
	s += ")"
	#print("INT adr %o iw %o op %d arg %d:" % (adr, iw, op, arg), l, s)
	x = p.t.add(adr, ea, "domus_int")
	x.render = s

