#!/usr/local/bin/python
#

from __future__ import print_function

import mem_domus
import cpu_domus
import file_domus

def int_getparams(p, adr, args):
	print("GETPARMS @%o" % args[0], args)

	a0 = args[0]
	cpu_domus.dot_txt(p, a0 + 0o527, a0 + 0o532)
	cpu_domus.dot_txt(p, a0 + 0o533, a0 + 0o535)
	cpu_domus.dot_txt(p, a0 + 0o536, a0 + 0o540)
	cpu_domus.dot_txt(p, a0 + 0o552, None)

	a0 = args[1] >> 1
	a = a0
	while True:
		b = p.m.rd(a)
		if b >> 8 == 0xff:
			break;
		print("%04x" % p.m.rd(a))
		cpu_domus.dot_txt(p, a, a + 3)
		a += 3

def int_p0090(p, adr, args):
	a0 = args[0]
	print("P0090(%o)" % a0)
	p.todo(a0 + 4, p.cpu.disass)


dn = "/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"

libx= ( "CODEP", "CODEX", "ULIB", "FSLIB",)

codeprocs = {
"FSLIB::RANDM":	(None,	"RANDM", "A", "N"),
"FSLIB::CHECK":	(None,	"CHECK", "A", "A", "A", "A", "A", "N"),
"CODEP::ADMME":	(None,	"ADMME", "A", "A", "V", "N"),
"CODEP::BUFFE":	(None,	"BUFFE", "A", "V", "A", "A", "V", "N"),
"CODEP::CHANG":	(None,	"CHANG", "A", "A", "N"),
"CODEP::FILL":	(None,	"FILL", "V", "A", "V", "V", "N"),
"CODEP::GETER": (None, "GETER", "A", "V", "A", "A", "N"),
"CODEP::LOAD": (None, "LOAD", "A", "V", "N"),
"CODEP::OPERA":	(None,	"OPERA", "A", "N"),
"CODEP::P0007": (None, "P0007", "A", "A", "N"),
"CODEP::P0023": (None, "P0023", "V", "N"),
"CODEP::P0039": (None, "P0039", "A", "A", "A", "N"),
"CODEP::P0040": (None, "P0040", "A", "V", "N"),
"CODEP::P0054":	(None,	"P0054", "A", "V", "N"),
"CODEP::P0076":	(None,	"P0076", "A", "A", "N"),
"CODEP::P0084": (None, "FINIS", "V",),
"CODEP::P0085": (None, "P0085", "A", "A", "A", "N"),
"CODEP::P0086": (None, "P0086", "A", "V", "A", "N"),
"CODEP::P0087":	(None,	"P0087", "V", "A", "N"),
"CODEP::P0088": (None, "P0088", "A", "A", "V", "V", "V", "N"),
"CODEP::P0089":	(None,	"P0089", "A", "V", "V", "V", "N"),
"CODEP::P0090": (int_p0090, "P0090", "N" ),
"CODEP::P0091": (None, "P0091", "A", "A", "V", "N"),
"CODEP::P0092":	(None,	"P0092", "V", "V", "A", "A", "N"),
"CODEP::P0093":	(None,	"P0093", "V", "A", "N"),
"CODEP::P0095":	(None,	"P0095", "A", "V", "A", "N"),
"CODEP::P0098":	(None,	"P0098", "A", "N"),
"CODEP::P0121":	(None,	"P0121", "V", "V", "V", "N"),
"CODEP::P0122":	(None,	"P0122", "A", "V", "V", "N"),
"CODEP::P0123":	(None,	"P0123", "A", "A", "V", "N"),
"CODEP::P0124":	(None,	"P0124", "V", "A", "V", "N"),
"CODEP::P0127":	(None,	"P0127", "A", "N"),
"CODEP::P0128":	(None,	"P0128", "A", "N"),
"CODEP::P0130": (None, "P0130", "A", "V", "V", "V", "V", "N"),
"CODEP::P0132": (None, "P0132", "A", "A", "N"),
"CODEP::P0150": (None, "P0150", "A", "N"),
"CODEP::P0154": (None, "P0154", "A", "A", "N"),
"CODEP::P0159": (None, "P0150", "A", "A", "N"),
"CODEP::P0160": (None, "P0160", "A", "V", "V", "V", "N"),
"CODEP::P0161": (None, "P0161", "V", "A", "V", "V", "N"),
"CODEP::P0167": (None, "P0167", "A", "A", "A", "N"),
"CODEP::P0168": (None, "P0168", "A", "A", "A", "N"),
"CODEP::P0169": (None, "P0169", "A", "A", "A", "N"),
"CODEP::P0170": (None, "P0170", "A", "A", "A", "A", "N"),
"CODEP::P0230": (None, "P0230", "A", "V", "N"),
"CODEP::P0237": (None, "P0237", "V", "N"),
"CODEP::P0238": (None, "P0237", "V", "N"),
"CODEP::P0239": (None, "P0239", "A", "A", "V", "V", "N"),
"CODEP::P0260": (int_getparams, "GETPARAMS", "A", "A", "A", "A", "V", "N"),
"CODEP::P0263": (None, "GETNAME", "A", "A", "A", "N"),
"CODEP::P0XXX":	(None, "P0XXX", "A", "N"),
"CODEP::PYY86":	(None, "PYY86", "A", "V", "A", "A", "N"),
"CODEP::RANDO":	(None,	"RANDO", "A", "V", "N"),
"CODEP::SPRIO":	(None,	"SPRIO", "A", "A", "V", "N"),
"CODEP::STORE": (None, "STORE", "A", "V", "N"),
#CODEP::P0261": (None, "CONNECTFILE", ...RCSL-43-GL-10639
#CODEP::P0262": (None, "SPLITSHARE", ...RCSL-43-GL-10639
#CODEP::P0264": (None, "GETERROR", ...RCSL-43-GL-10639
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
			x = p.t.add(adr, adr + 1 + df.max_nrel - oo, "CodeProc")
			x.blockcmt += "CODE PROCEDURE " + i + " FROM " + ll + "\n"
			p.setlabel(adr, i)
			if idx in codeprocs:
				x.blockcmt += str(codeprocs[idx]) + "\n"
				return codeprocs[idx]
			return None

def int_opmess(p, adr, args):
	a = args[0]>>1
	try:
		b = p.m.rd(a)
		cpu_domus.dot_txt(p, a, None)
	except:
		pass

def int_outtext(p, adr, args):
	a = args[1]>>1
	try:
		b = p.m.rd(a)
		cpu_domus.dot_txt(p, a, None)
	except:
		pass

def int_link(p, adr, args):
	print("LINK %o" % adr, "%o" % args[0])
	x = p.t.add(args[0], adr + 2, "MUSIL_FUNC")
	x.blockcmt += "\nMUSIL FUNCTION\n"

intins = {

0:	( None, "STOP", ),

1:	( None, "ANDD", "ARG", "N"),
2:	( None, "LOADD", "ARG", "N"),
3:	( None, "+D", "ARG", "N"),
4:	( None, "-D", "ARG", "N"),
5:	( None, "SHIFTD", "ARG", "N"),
6:	( None, "EXTRACTD", "ARG", "N"),
7:	( None, "*D", "ARG", "N"),
8:	( None, "/D", "ARG", "N"),

9:	( None, "ANDC", "CONST", "N"),
10:	( None, "LOADC", "CONST", "N"),
11:	( None, "+C", "CONST", "N"),
12:	( None, "-C", "CONST", "N"),
13:	( None, "SHIFTC", "CONST", "N"),
14:	( None, "EXTRACTC", "CONST", "N"),
15:	( None, "*C", "CONST", "N"),
16:	( None, "/C", "CONST", "N"),

17:	( None, "AND", "ADDR", "N"),
18:	( None, "LOAD", "ADDR", "N"),
19:	( None, "+", "ADDR", "N"),
20:	( None, "-", "ADDR", "N"),
21:	( None, "SHIFT", "ADDR", "N"),
22:	( None, "EXTRACT", "ADDR", "N"),
23:	( None, "*", "ADDR", "N"),
24:	( None, "/", "ADDR", "N"),

25:	( None, "LOAD_NEGATIVE", "V", "N"),
26:	( None, "LOAD_BYTE", "A", "N"),
27:	( None, "LOAD_BYTEWORD", "A", "N"),
28:	( None, "JUMP", "JUMP", "N"),
29:	( int_link, "LINK", "LN"),
30:	( None, "MOVEWORD", ">>2", "ADDR", "V", "N"),
31:	( None, "MOVESTRING", "A", "A", "V", "N"),
32:	( None, "??COMPAREWORD",),
33:	( None, "COMPARESTRING", "A", "A", "V", "N"),
34:	( None, "STORE_REGSITER", "ADDR", "N"),
35:	( None, "TRANSLATE", "A", "A", "A", "N"),
36:	( None, "CONVERT", "A", "A", "A", "V", "N"),
37:	( int_opmess, "OPMESS", "A", "N"),
38:	( None, "OPIN", "A", "N"),
39:	( None, "OPWAIT", "ADDR", "N"),
40:	( None, "CALL", "CL", "N"),
41:	( None, "OPTEST", "N"),
42:	( None, "MOVE", "BITS", "A", "V", "A", "V", "V", "N"),
43:	( None, "OPSTATUS",),
44:	( None, "BINDEC", "V", "A", "N"),
45:	( None, "DECBIN", "A", "ADDR", "N"),
46:	( None, "CHAR", "V", "A", "V", "N"),
47:	( None, "GOTO", ),
48:	( None, "GO_CODE", "GC" ),

49:	( None, "OP49", "V", "N"),
50:	( None, "OP50", "A", "N"),
51:	( None, "OP51", "I", ),
52:	( None, "OP52", ),
53:	( None, "OP53", ),
54:	( None, "OP54", ),
55:	( None, "OP55", "I", "N"),
56:	( None, "OP56", "A", "V", "N"),
57:	( None, "OP57", "A", "V", "N"),

128:	( None, "GETREC", "ZONE", "ADDR", "N"),
129:	( None, "PUTREC", ">>2", "ADDR", "V", "N"),
130:	( None, "WAITTRANSFER", "ZONE", "N"),
131:	( None, "REPEATSHARE", "ZONE", "N"),
132:	( None, "TRANSFER", "ZONE", "V", "V", "N"),
133:	( None, "INBLOCK", "ZONE", "N"),
134:	( None, "OUTBLOCK", "ZONE", "N"),
135:	( None, "FREESHARE", "ZONE", "ADDR", "N"),
136:	( None, "INCHAR", "ZONE", "N"),
137:	( None, "OUTSPACE", "ZONE", "N"),
138:	( None, "OUTCHAR", ">>2", "ADDR", "V", "N"),
139:	( None, "OUTNL", "N"),
140:	( None, "OUTEND", "V", "N"),
141:	( int_outtext, "OUTTEXT",	"ZONE", "A", "N"),
142:	( None, "OUTOCTAL",),
143:	( None, "SETPOS",	"ZONE", "V", "V", "N"),
144:	( None, "CLOSE",	"ZONE", "V", "N"),
145:	( None, "OPEN",	"ZONE", "V", "N"),
146:	( None, "WAITZONE",	"ZONE", "N"),

218:	( None, "NEWCAT",	">>2", "A", "V", "N"),
219:	( None, "FREECAT",	">>2", "A", "N"),

230:	( None, "CREATEENTRY", "ZONE", "V", "V", "N"),
231:	( None, "LOOKUPENTRY", "ZONE", "A", "N"),
232:	( None, "CHANGEENTRY", "ZONE", "A", "N"),
233:	( None, "REMOVEENTRY", "ZONE", "N"),
234:	( None, "INITCATALOG", "ZONE", "V", "V", "N"),
235:	( None, "SETENTRY", "ZONE", "A", "N"),
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
	s = l[1] + "("
	x = ""
	j = 2
	args = list()
	while j < len(l):
		i = l[j]
		j += 1
		t = None
		niw = p.m.rd(ea)
		if i == ">>2":
			arg >>= 2
		elif i == "BITS":
			arg = niw
			ea += 1
		elif i == "I":
			args.append(niw)
			t = ">%o" % niw
			ea += 1
			p.todo(niw, p.cpu.disass)
		elif i == "ARG":
			args.append(arg)
			t = "%o" % arg
		elif i == "JUMP":
			args.append(niw)
			t = "CC=%o, %o" % (arg, niw)
			p.todo(niw, disass)
			ea += 1
		elif i == "CONST":
			args.append(niw)
			t = "%o" % niw
			ea += 1
		elif i == "ZONE":
			args.append(niw)
			t = "zone=%o" % niw
			p.todo(niw, p.cpu.zonedesc)
			za = p.m.rd(niw + 3)
			p.todo(za, p.cpu.disass)
			arg >>= 2
			ea += 1
		elif i == "ADDR":
			args.append(niw)
			t = "%o" % niw
			ea += 1
		elif i == "A":
			tq = p.m.rdqual(ea)
			ea += 1
			if tq == 3:
				ax = "%o'*2" % (niw >> 1)
				if niw & 1:
					ax += "+1"
			else:
				ax = "%o" % niw + p.m.qfmt(tq)
			args.append(niw)
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
				args.append(niw)
				t = "V0: %o" % niw
				ea += 1
			elif arg & 3 == 1:
				args.append('R')
				t = "V1: R"
			elif arg & 3 == 2:
				args.append(niw)
				t = "V2: (%o)" % niw
				ea += 1
			else:
				args.append('R')
				t = "V3: R"
			arg >>= 2
		elif i == "LN":
			args.append(niw)
			t = "%o" % niw
			ea += 1
		elif i == "CL":
			args.append(niw)
			t = "%o" % niw
			ea += 1
			p.todo(niw, p.cpu.disass)
		elif i == "GC":
			if not 'musil_code' in p.a:
				p.a['musil_code'] = dict()
			y = p.a['musil_code']

			pd = p.a['procdesc']
			ta = p.m.rd(pd - arg)

			func=arg
			t = "[%d]=%o" % (-func, ta)
			arg = niw
			ea += 1
			t += ", %o" % arg
			p.todo(ta, p.cpu.disass)
			if not func in y:
				xx = ident_lib_module(p, ta)
				if xx != None:
					y[func] = xx
			if func in y:
				t += ", " + y[func][1]
				l += y[func][2:]
				l = (y[func][0],) + l[1:]
				args.append(ta)
			else:
				print("CODE %d at %o unknown args" % (func, ta))
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
	if l[0] != None:
		l[0](p, adr, args)
	x = p.t.add(adr, ea, "domus_int")
	x.render = s

