#!/usr/local/bin/python
#
# Read MUPAR file and emit two files with special instructions and
# page zero symbols
#

from __future__ import print_function

fi = open("/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rcsrc/MUPAR", "r")

loc = -1
syms = dict()
tsyms = dict()
vsyms = dict()

def subexpr(x):
	v = 0
	#print("SUBEXPR:", x)
	while len(x) > 0:
		if x[0].isspace():
			x = x[1:]
			continue
		if x[:4] == "JSR@":
			v = 0x0c00
			x,s = subexpr(x[4:])
			v |= s
			continue
		if x[:4] == "JMP@":
			v = 0x0400
			x,s = subexpr(x[4:])
			v |= s
			continue
		if x[:1] == "@":
			v = 0x8000
			x,s = subexpr(x[1:])
			v |= s
			continue
		if x[0].isdigit():
			v *= 10
			v += int(x[0])
			x = x[1:]
		elif x[0] == "+":
			x,s = subexpr(x[1:])
			v += s
		elif x[0] == "-":
			x,s = subexpr(x[1:])
			v -= s
		else:
			for i in range(0, len(x)):
				c = x[i]
				if c.isupper() or \
				    (i > 0 and c.isdigit()) or \
				    c == "." or c == "_" or c == "?":
					pass
				else:
					break
				if i + 1 == len(x):
					i += 1
					break
			j = i
			if j > 5:
				j = 5
			if x[:j] in tsyms:
				assert v == 0
				v = tsyms[x[:j]]
				x = x[i:]
			else:
				print("???", x)
				x = x[1:]
				exit(2)
	return (x, v)

def expr(x):
	y,v = subexpr(x)
	assert y == ""
	#print("EXPR <%s> = %o" % (x, v))
	return v

for i in fi.readlines():
	j = i.find(';')
	if j != -1:
		i = i[:j]
	i = i.strip()
	if i == "":
		continue
	j = i.split(None, 1)
	if j[0] == ".TITL":
		assert j[1] == "MUPAR"
	elif j[0] == ".RDX":
		rdx = int(j[1])
		assert rdx == 10
	elif j[0] == ".END":
		break
	elif j[0] == ".LOC":
		# We mark definitions based on .loc directives with 0x10000
		tsyms["."] = expr(j[1]) | 0x10000
	elif j[0] == ".DUSR":
		(sym,exp) = j[1].split('=', 1)
		sym = sym.strip()
		exp = exp.strip()
		assert sym not in syms
		v = expr(exp)
		syms[sym] = v
		tsyms[sym[:5]] = v
		if v not in vsyms:
			vsyms[v] = sym
		#print("SYM[%s]=%06o" % (sym,v))
	else:
		print(j)
		exit (2)
fi.close()

fof = open("domus_funcs.txt", "w")
fopz = open("domus_page_zero.txt", "w")
for f in (fof, fopz):
	f.write("# Machine generated file, see rd_mupar.py\n\n")

#############################################################################
# Manual fixups

vsyms[0x10020] = "CUR"

for i in sorted(vsyms.keys()):
	#print("%05x %06o %s" % (i, i, vsyms[i]))
	if i >= 0x10000 and i <= 0x10100:
		fopz.write("%s 0x%04x\n" % (vsyms[i], i & 0xffff))
	elif i >= 0x10400 and i < 0x11000:
		fof.write('%-20s "" ' % vsyms[i])
		for j in range (15,-1,-1):
			fof.write("|%d" % ((i >> j) & 1))
		fof.write("|\n")
