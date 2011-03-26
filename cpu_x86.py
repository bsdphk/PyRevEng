#!/usr/local/bin/python
#
# Intel x86 family CPU disassembler
#

from __future__ import print_function

import mem

class X86Error(Exception):
        def __init__(self, adr, reason):
                self.adr = adr
                self.reason = reason
                self.value = ("0x%x:" % adr + str(self.reason),)
        def __str__(self):
                return repr(self.value)
shortform = {
	# Args in same order as manual
	0x06:	("push",	( "ES",),	None),
	0x07:	("pop",		( "ES",),	None),
	0x16:	("push",	( "SS",),	None),
	0x17:	("pop",		( "SS",),	None),
	0x0e:	("push",	( "CS",),	None),
	0x1e:	("push",	( "DS",),	None),
	0x1f:	("pop",		( "DS",),	None),
	0x27:	("daa",		( None,),),
	0x60:	("pusha",	( None,),	None,	),
	0x61:	("popa",	( None,),	None,	),
	0x68:	("push",	( "Iz",),	None),
	0x69:	("imul",	( "Gv", "Ev", "Iz"),),
	0x6a:	("push",	( "Ib",),	None),
	0x6b:	("imul",	( "Gv", "Ev", "Ib"),),
	0x6c:	(("ins","insb"),( "Yb",	"DX"),	None),
	0x6d:	("insw",	( "Yz",	"DX"),	None),
	0x6e:	(("outs","outsb"),( "DX",	"Xb"),	None),
	0x6f:	("outsw",	( "DX",	"Xz"),	None),
	0x80:	("$alu",	( "Eb", "Ib"),	8,	True),
	0x81:	("$alu",	( "Ev", "Iz"),	0,	True),
	0x83:	("$alu",	( "Ev", "Ib"),	0,	True),
	0x84:	("test",	( "Eb",	"Gb"),),
	0x85:	("test",	( "Ev",	"Gv"),),
	0x86:	("xchg",	( "Eb", "Gb"),),
	0x87:	("xchg",	( "Ev", "Gv"),),
	0x88:	("mov",		( "Eb",	"Gb"),),
	0x89:	("mov",		( "Ev",	"Gv"),),
	0x8a:	("mov",		( "Gb",	"Eb"),),
	0x8b:	("mov",		( "Gv",	"Ev"),),
	0x8e:	("mov",		( "Sw",	"Ew"),	16,	True),
	0x90:	("nop",		( None,),),
	0x99:	("cltd",	( None,),),
	0x9b:	("fwait",	( None,),),
	0x9c:	("pushf",	( None,),	None,	True),
	0x9d:	("popf",	( None,),	None,	True),
	0xa0:	("mov",		( "AL",	"Ob"),	None),
	0xa1:	("mov", 	( "rAX","Ov"),	None),
	0xa2:	("mov", 	( "Ob", "AL"),	None),
	0xa3:	("mov", 	( "Ov", "rAX"),	None),
	0xa4:	("movsb", 	( "Yb", "Xb"),	None),
	0xa5:	("movsw", 	( "Yv", "Xv"),	None),
	0xa6:	("cmpsb", 	( "Xb", "Yb"),	None),
	0xa7:	("cmpsw", 	( "Xv", "Yv"),	None),
	0xa8:	("test",	( "AL",	"Ib"),	None),
	0xa9:	("test",	( "rAX","Iz"),	None),
	0xaa:	("stos",	( "Yb",	"AL"),	None),
	0xab:	("stos",	( "Yv",	"rAX"),	None),
	0xac:	("lods",	( "AL",	"Xb"),	None),
	0xad:	("lods",	( "rAX","Xv"),	None),
	0xae:	("scasb",	( "AL",	"Yb"),	None),
	0xaf:	("scasw",	( "rAX","Yv"),	None),
	0xc0:	("$shifts",	( "Eb",	"Ib"),	8,	True),
	0xc1:	("$shifts",	( "Ev",	"Ib"),	0,	True),
	0xc8:	("enter",	( "Ib", "Iw"),	None),
	0xc9:	("leave",	( None,),),
	0xcc:	("int3",	( None,),),
	0xd0:	("$shifts",	( "Eb",),	8,	True),
	0xd1:	("$shifts",	( "Ev",),	0,	True),
	0xd2:	("$shifts",	( "Eb", "CL"),	8,	True),
	0xd3:	("$shifts",	( "Ev", "CL"),	0,	True),
	0xd4:	("aam",		( "Ib",),	None),
	0xe4:	("in",		( "AL",	"Ib"),	None),
	0xe5:	("in",		( "eAX","Ib"),	None),
	0xe6:	("out",		( "Ib",	"AL"),	None),
	0xe7:	("out",		( "Ib",	"eAX"),	None),
	0xec:	("in",		( "AL",	"DX"),	None),
	0xed:	("in",		( "eAX","DX"),	None),
	0xee:	("out",		( "DX",	"AL"),	None),
	0xef:	("out",		( "DX",	"eAX"),	None),
	0xf1:	("icebp",	( None,),),
	0xf3:	("repz",	( None,),),
	0xf8:	("clc",		( None,),),
	0xf9:	("stc",		( None,),),
	0xfa:	("cli",		( None,),),
	0xfb:	("sti",		( None,),),
	0xfc:	("cld",		( None,),),
	0x0f08:	("invd",	( None,),),
	0x0f09:	("wbinvd",	( None,),),
	0x0f20:	("mov",		( "Rd/q","Cd/q"),),
	0x0f22:	("mov",		( "Cd/q","Rd/q"),),
	0x0f30:	("wrmsr",	( None,),),
	0x0f31:	("rdtsc",	( None,),),
	0x0f32:	("rdmsr",	( None,),),
	0x0f6e: ("movd",	( "Pq",	"Ed/q"),),
	0x0f77:	("emms",	( None,),),
	0x0f94:	("sete",	( "Eb",),),
	0x0f95:	("setne",	( "Eb",),),
	0x0fa2:	("cpuid",	( None,),),
	0x0fac:	("shrd",	( "Ev", "Gv", "Ib"),),
	0x0faf:	("imul",	( "Gv",	"Ev"),),
	0x0fbc:	("bsf",		( "Gv",	"Ev"),),
}

opersz = {
	"AL":	8,
	"Eb":	8,
	"Gb":	8,
	"Ew":	16,
	"Sw":	16,
}

class x86(object):
	def __init__(self, mode):
		self.setmode(mode)
		self.syntax = "att"
		self.immpfx = "$"

		# Vol3 p364

		self.reg8 = ( "%al",  "%cl",  "%dl",  "%bl",
		    "%ah",  "%ch",  "%dh",  "%bh")
		self.reg16 = ("%ax",  "%cx",  "%dx",  "%bx",
		     "%sp",  "%bp",  "%si",  "%di")
		self.reg32 = ("%eax", "%ecx", "%edx", "%ebx",
		    "%esp", "%ebp", "%esi", "%edi")
		self.sReg = ( "%es",  "%cs",  "%ss",  "%ds",
		     "%fs",  "%gs",  None,   None)
		self.cReg = ( "%cr0", "%cr1", "%cr2", "%cr3",
		    "%cr4", "%cr5", "%cr6", "%cr7")

		self.gReg = { 8:  self.reg8, 16: self.reg16, 32: self.reg32, }
		self.xReg = { 16: "(%si)", 32: "(%esi)" }
		self.yReg = { 16: "(%di)", 32: "(%edi)" }

		self.mReg = "%mm"
		self.dReg = "(%dx)"

		self.cc=("o", "no", "b", "nb", "z", "nz", "be", "nbe", 
		    "s", "ns", "p", "np", "l", "nl", "le", "nle")

		self.shifts=("rol", "ror", "rcl", "rcr",
		    "shl", "shr", "sal", "sar")
		self.alu=(   "add", "or",  "adc", "sbb",
		    "and", "sub", "xor", "cmp")

		self.modrm16 = ("%bx+%si", "%bx+%di", "%bp+%si", "%bp+%di",
			   "%si", "%di", "%bp", "%bx")

	def setmode(self, mode):
		if mode == "real":
			self.mosz=16
			self.masz=16
			self.arch="i8086"
		elif mode == "32bit":
			self.mosz=32
			self.masz=32
			self.arch="i386"
		else:
			assert False

		self.mode = mode

	def render(self, p, t, lvl):
		s = t.a['mne']
		if type(s) != str:
			print("XXX: @%x mne:" % t.start, s)
			return("XXX BOGUS mne XXX", )
		if 'oper' in t.a:
			s += "\t"
			d = ""
			for i in t.a['oper']:
				s += d
				s += str(i)
				d = ','
		return (s,)

	def unknown(self, p, adr):
		from subprocess import check_output

		j=bytearray()
		for i in range(0,15):
			try:
				j.append(p.m.rd(self.ia + i))
			except:
				break

		f = open("/tmp/_x86.bin", "wb")
		f.write(j)
		f.close()
		print("--------------------------------------------------")
		r = check_output("objdump -b binary -D -mi386 -M" + self.arch +
		    " /tmp/_x86.bin", shell=True)
		print(r.decode('ascii'))
		print("--------------------------------------------------")

	def modRM(self, p):
		assert self.mrm == None

		modrm = p.m.rd(self.na)
		self.na += 1
		mod = modrm >> 6
		reg = (modrm >> 3) & 7
		rm = modrm & 7
		self.mrm = (mod, reg, rm)

	def ea(self, p, hint=None):
		if hint != None and hint[1] == 'b':
			mosz = 8
		elif hint != None and hint[1] == 'w':
			mosz = 16
		else:
			mosz = self.osz

		ea = self.seg
		l = None

		if self.mrm[0] == 3:
			ea = self.gReg[mosz][self.mrm[2]]
			return ea

		if self.asz == 16:
			if self.mrm[0] == 0 and self.mrm[2] == 6:
				x = p.m.s16(self.na)
				self.na += 2
				ea += "%d" % x
				return ea
			else:
				rx = "(" + self.modrm16[self.mrm[2]]
		elif self.asz == 32:
			if self.mrm[2] == 4:
				sip = p.m.rd(self.na)
				self.na += 1
				sip_s = 1 << (sip >> 6)
				sip_i = (sip >> 3) & 7
				sip_b = sip & 7
				self.sip = (sip_s, sip_i, sip_b)
				if self.mrm[0] == 0 and sip_b == 5:
					rx = "0x%x(" % p.m.w32(self.na)
					self.na += 4
				else:
					rx = "(" + self.reg32[sip_b]
				if sip_i != 4:
					rx += "," + self.reg32[sip_i]
					rx += ",%d" % sip_s
			elif self.mrm[0] == 0 and self.mrm[2] == 5:
				rx = "0x%x" % p.m.w32(self.na)
				self.na += 4
			else:
				rx = "(" + self.reg32[self.mrm[2]]
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if self.mrm[0] == 0:
			ea = self.seg + rx
			f = None
		elif self.asz == 16 and self.mrm[0] == 1:
			x = p.m.s8(self.na)
			self.na += 1
			f = "%d"
		elif self.mrm[0] == 1:
			x = p.m.rd(self.na)
			self.na += 1
			if x & 0x80:
				x |= 0xffffff00
			f = "0x%02x"
		elif self.mrm[0] == 2 and self.asz == 16:
			x = p.m.w16(self.na)
			self.na += 2
			f = "0x%04x"
		elif self.mrm[0] == 2 and self.asz == 32:
			x = p.m.w32(self.na)
			self.na += 4
			f = "0x%08x"
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if self.asz == 16 and f != None:
			f = "%d"
			ea += f % x + rx
		elif f != None:
			f = "0x%x"
			ea += f % x + rx
		if ea.find("(") > -1:
			ea += ")"
		return ea

	def dir(self, p, sz):
		if sz == 8:
			w =  p.m.rd(self.na)
			self.na += 1
			return ("0x%x" % w, w)
		if sz == 16:
			w =  p.m.w16(self.na)
			self.na += 2
			return ("0x%x" % w, w)
		if sz == 32:
			w =  p.m.w32(self.na)
			self.na += 4
			return ("0x%x" % w, w)
		raise X86Error(self.na, "Wrong dir width (%d)" % sz)

	def imm(self, p, sz, se = False):
		#print("IMM", p, sz, se)
		if sz == 8:
			f = self.immpfx + "0x%02x"
			v = p.m.rd(self.na)
			if v & 0x80 and self.osz > 8:
				v |= 0xffffff00
			self.na += 1
		elif sz == 16:
			f = self.immpfx + "0x%04x"
			v = p.m.w16(self.na)
			self.na += 2
		elif sz == 32:
			f = self.immpfx + "0x%08x"
			v = p.m.w32(self.na)
			self.na += 4
		else:
			raise X86Error(self.na, "Wrong imm width (%d)" % sz)
		f = self.immpfx + "0x%x"
		return f % v

	def fmarg(self, p, i):
		if i == None:
			return
		elif i == "AL":
			self.o.append(self.reg8[0])
		elif i == "AH":
			self.o.append(self.reg8[4])
		elif i == "BL":
			self.o.append(self.reg8[3])
		elif i == "eAX":
			# XXX: is this a type for rAX ?
			self.o.append(self.gReg[self.osz][0])
		elif i == "rAX":
			self.o.append(self.gReg[self.osz][0])
		elif i == "Cd/q":
			self.o.append(self.cReg[self.mrm[1]])
		elif i == "CL":
			self.o.append(self.reg8[1])
		elif i == "CS":
			self.o.append(self.sReg[1])
		elif i == "DX":
			self.o.append(self.dReg)
		elif i == "DS":
			self.o.append(self.sReg[3])
		elif i == "ES":
			self.o.append(self.sReg[0])
		elif i == "Ib":
			self.o.append(self.imm(p, 8))
		elif i == "Iw":
			self.o.append(self.imm(p, 16))
		elif i == "Iz":
			self.o.append(self.imm(p, self.osz))
		elif i == "Eb":
			self.o.append(self.ea(p, i))
		elif i == "Ev":
			self.o.append(self.ea(p, i))
		elif i == "Ew":
			self.o.append(self.ea(p, i))
		elif i == "Ed/q":
			self.o.append(self.ea(p))
		elif i == "Gv":
			self.o.append(self.gReg[self.osz][self.mrm[1]])
		elif i == "Gb":
			self.o.append(self.gReg[8][self.mrm[1]])
		elif i == "Ms":
			# XXX: must be memory
			self.o.append(self.ea(p))
		elif i == "Rd/q":
			if self.mrm[0] != 3:
				raise X86Error(self.ia, "Rd/q mod!=3")
			self.o.append(self.gReg[32][self.mrm[2]])
		elif i == "Ob":
			x = self.dir(p, self.asz)
			self.o.append(x[0])
		elif i == "Ov":
			x = self.dir(p, self.asz)
			self.o.append(x[0])
		elif i == "Pq":
			self.o.append(self.mReg + "%d" % self.mrm[1])
		elif i == "SS":
			self.o.append(self.sReg[2])
		elif i == "Sw":
			self.o.append(self.sReg[self.mrm[1]])
		elif i[0] == "X":
			if self.seg != "":
				s = self.seg
			else:
				s = self.sReg[3] + ":"
			self.o.append(s + self.xReg[self.asz])
		elif i[0] == "Y":
			if self.seg != "":
				s = self.seg
			else:
				s = self.sReg[0] + ":"
			self.o.append(s + self.yReg[self.asz])
		else:
			raise X86Error(self.ia,
			    "Unknown short (%s)" % str(i))


	def sfrm(self, p, mne, args, suff=None, wid=0):
		self.short = (mne, args, suff, self.osz, self.asz)
		self.mne = mne

		if self.asz != self.masz:
			self.mne = "addr32 " + self.mne

		if suff != None:
			if self.mrm != None and self.mrm[0] == 3 and suff != "*":
				pass
			elif args[0] == "Sw":
				self.mne += "w"
			elif len(args) > 1 and args[1] == "Iz" and self.osz == 16:
				self.mne += "w"
			elif len(args) > 1 and args[1] == "Ib" and self.osz == 16:
				self.mne += "w"
			elif len(args) > 1 and args[1] == "Sw":
				self.mne += "w"
			elif self.osz == 32:
				self.mne += "l"
			elif self.osz == 16:
				self.mne += "w"
			elif self.osz == 8:
				self.mne += "b"
			else:
				assert False

		x = list(args)
		while len(x) < 2:
			x.append(None)
		src = x[0]
		dst = x[1]
		for i in x:
			self.fmarg(p, i)
		self.o.reverse()

	def setargs(self, a, b):
		self.o.append(a)
		self.o.append(b)

	def __decode(self, p):

		iw = p.m.rd(self.na)
		self.na += 1

		try:
			iw2 = p.m.rd(self.na)
			if iw == 0xff and iw2 == 0xff:
				return None
			if iw == 0x00 and iw2 == 0x00:
				return None
		except:
			pass

		#print(">> 0x%x: %x " % (adr, iw))

		# Prefixes
		while True:
			if iw == 0x66:
				self.osz = 48 - self.osz
			elif iw == 0x67:
				self.asz = 48 - self.asz
			elif iw == 0x26:
				self.seg = self.sReg[0] + ":"
			elif iw == 0x2e:
				self.seg = self.sReg[1] + ":"
			elif iw == 0x3e:
				self.seg = self.sReg[3] + ":"
			elif iw == 0x64:
				self.seg = self.sReg[4] + ":"
			elif iw == 0x65:
				self.seg = self.sReg[5] + ":"
			else:
				break
			iw = p.m.rd(self.na)
			self.na += 1

		# Two-byte instructions
		if iw == 0x0f or iw == 0xdb:
			iw <<= 8
			iw |= p.m.rd(self.na)
			self.na += 1

		if iw in shortform:
			ss = shortform[iw]
			mne = ss[0]
			arg = ss[1]

			if len(ss) > 3:
				suf = ss[3]
			else:
				suf = None

			if len(ss) > 2 and ss[2] == None:
				# Explicitly: No ModRM byte
				pass
			elif len(ss) > 2 and ss[2] != 0:
				assert type(ss[2]) == int
				wid = ss[2]
				self.osz = wid
				self.modRM(p)
			elif arg[0] == None:
				# No args, no ModRM
				pass
			else:
				for i in arg:
					if i in opersz:
						self.osz = opersz[i]
				self.modRM(p)

			if self.mrm == None:
				i = (p.m.rd(self.na) >> 3) & 7
			else:
				i = self.mrm[1]
			if mne == "$shifts":
				mne = self.shifts[i]
			elif mne == "$alu":
				mne = self.alu[i]
			elif type(mne) != str:
				if self.syntax == "intel":
					mne = mne[0]
				else:
					mne = mne[1]
			self.sfrm(p, mne, arg, suf)
		elif 0x00 == iw & 0xffcc:
			if not iw & 1:
				self.osz = 8
			self.modRM(p)
			self.sfrm(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    (("Eb",  "Ev",  "Gb",  "Gv" )[iw & 3],
			    ("Gb",  "Gv",  "Eb",  "Ev" )[iw & 3]))
		elif 0x04 == iw & 0xffcf:
			self.osz = 8
			self.sfrm(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    ("AL", "Ib"))
		elif 0x05 == iw & 0xffcf:
			self.sfrm(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    ("rAX", "Iz"))
		elif 0x08 == iw & 0xffcc:
			if not iw & 1:
				self.osz = 8
			self.modRM(p)
			self.sfrm(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    (("Eb",  "Ev",  "Gb",  "Gv" )[iw & 3],
			    ("Gb",  "Gv",  "Eb",  "Ev" )[iw & 3]))
		elif 0x0c == iw & 0xffcf:
			self.osz = 8
			self.sfrm(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    ("AL", "Ib"))
		elif 0x0d == iw & 0xffcf:
			self.sfrm(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    ("rAX", "Iz"))
		elif 0x40 == iw & 0xfff8:
			self.mne ="inc"
			self.o.append(self.gReg[self.osz][iw & 0x07])
		elif 0x48 == iw & 0xfff8:
			self.mne ="dec"
			self.o.append(self.gReg[self.osz][iw & 0x07])
		elif 0x50 == iw & 0xfff8:
			self.mne ="push"
			self.o.append(self.gReg[self.osz][iw & 0x07])
		elif 0x58 == iw & 0xfff8:
			self.mne ="pop"
			self.o.append(self.gReg[self.osz][iw & 0x07])
		elif 0x70 == iw & 0xfff0:
			#  ['Jcc', 'rel8off', '75', 'cb', '\n']
			cx = self.cc[iw & 0xf]
			self.mne = "j" + cx
			da = self.ia + 2 + p.m.s8(self.ia + 1)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow = (
			    ('cond', cx, da),
			    ('cond', self.cc[(iw ^ 1) & 0xf], self.ia + 2)
			)
		elif 0x8c == iw:
			#  ['MOV', 'reg16/32/64/mem16 segReg', '8C', '/r', '\n']
			self.mne = "mov"
			self.modRM(p)
			self.setargs (
				self.sReg[self.mrm[1]],
				self.ea(p)
			)
		elif 0x8d == iw:
			#  ['LEA', 'reg16 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg32 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg64 mem', '8D', '/r', '\n']
			self.mne = "lea"
			# XXX: osz or asz ?? 
			self.modRM(p)
			self.setargs(
			    self.ea(p),
			    self.gReg[self.osz][self.mrm[1]])
		elif 0x8f == iw:
			self.modRM(p)
			if self.mrm[1] == 0:
				self.mne = "ppp"
				self.o.append(self.ea(p))
		elif 0xb0 == iw & 0xfff8:
			self.osz = 8
			self.mne ="mov"
			self.setargs(
			    self.imm(p, 8),
			    self.reg8[iw & 7])
		elif 0xb8 == iw & 0xfff8:
			self.mne ="mov"
			self.setargs(
			    self.imm(p, self.osz),
			    self.gReg[self.osz][iw & 7])
		elif 0xc3 == iw:
			#  ['RET', '', 'E3', '', '\n']
			self.mne ="ret"
			self.flow = (('ret', 'T', None),)
		elif 0xc6 == iw:
			self.osz = 8
			self.modRM(p)
			if self.mrm[1] == 0:
				self.sfrm(p, 'mov', ('Eb', 'Ib'), True)
		elif 0xc7 == iw:
			self.modRM(p)
			if self.mrm[1] == 0:
				self.sfrm(p, 'mov', ('Ev', 'Iz'), True)
		elif 0xcb == iw:
			#  ['RET', '', 'E3', '', '\n']
			self.mne ="lret"
			self.flow = (('ret', 'T', None),)
		elif 0xcd == iw:
			#  ['INT', 'imm8', 'CD', 'ib', '\n']
			self.mne ="int"
			self.o.append(self.imm(p, 8))
			self.flow = (('call', 'T', None),)
		elif 0xcf == iw:
			self.mne ="iret"
			self.flow = (('ret', 'T', None),)
		elif 0xd9 == iw:
			# FP
			self.modRM(p)
			if self.mrm[0] != 3 and self.mrm[2] == 6:
				self.na += 1
				self.mne ="FNSTCW"
				self.o.append(self.imm(p, 16))
		elif 0xe0 == iw & 0xfffc:
			#  ['LOOP', 'rel8off', 'E2', 'cb', '\n']
			self.mne = ("loopne", "loope", "loop", "jcxz")[iw & 3]
			da = self.ia + 2 + p.m.s8(self.ia + 1)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow = (
			    ('cond', "XXX1", da),
			    ('cond', "XXX2",  self.na)
			)
		elif 0xe8 == iw:
			if self.asz == 16:
				oo = p.m.s16(self.na)
				self.na += 2
			elif self.asz == 32:
				oo = p.m.s32(self.na)
				self.na += 4
			else:
				assert False
			da = self.na + oo
			self.mne ="call"
			self.o.append("0x%x" % da)
			self.flow=(("call", "T", da),)
		elif 0xe9 == iw:
			#  ['JMP', 'rel16off', 'E9', 'cw', '\n']
			#  ['JMP', 'rel32off', 'E9', 'cd', '\n']
			self.mne ="jmp"
			if self.osz == 16:
				da = self.ia + 3 + p.m.s16(self.na)
				self.na += 2
			else:
				da = self.ia + 5 + p.m.s32(self.na)
				self.na += 4
			self.o.append("#0x%x" % da)
			self.flow=(('cond', 'T', da),)
		elif 0xea == iw:
			#  ['JMP', 'FAR pntr16:16', 'EA', 'cd', '\n']
			#  ['JMP', 'FAR pntr16:32', 'EA', 'cp', '\n']
			if self.asz == 16:
				off = p.m.w16(self.na)
				fx = "0x%04x"
				self.na += 2
			else:
				off = p.m.w32(self.na)
				fx = "0x%08x"
				self.na += 4
			sg = p.m.w16(self.na)
			self.na += 2
			if self.syntax == "intel":
				self.mne ="jmp"
				self.o.append("FAR")
				self.o.append("0x%04x" % sg)
				self.o.append(fx % off)
			else:
				self.mne ="ljmp"
				self.o.append("$0x%04x" % sg)
				self.o.append("$0x%x" % off)
			if self.mode == "real":
				self.flow=(('cond', 'T', (sg << 4) + off),)
			else:
				raise X86Error(self.ia, "EA not real mode")
		elif 0xeb == iw:
			#  ['JMP', 'rel8off', 'EB', 'cb', '\n']
			self.mne = "jmp"
			da = self.ia + 2 + p.m.s8(self.na)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow=(('cond', 'T', da),)
		elif 0xf4 == iw:
			self.mne ="hlt"
			self.flow = (('halt', 'T', None),)
		elif 0xf6 == iw:
			self.osz = 8
			self.modRM(p)
			if self.mrm[1] < 2:
				self.sfrm(p, "test", ("Eb", "Ib"), True)
			else:
				self.sfrm(p,
				    ("", "", "not", "neg", "mul", "imul",
				    "div", "idiv")[self.mrm[1]],
				    ("Eb",), True)
		elif 0xf7 == iw:
			self.modRM(p)
			if self.mrm[1] < 2:
				self.sfrm(p, "test", ("Ev", "Iz"), True)
			else:
				self.sfrm(p,
				    ("", "", "not", "neg", "mul", "imul",
				    "div", "idiv")[self.mrm[1]],
				    ("Ev",), True)
		elif 0xfe == iw:
			self.osz = 8
			self.modRM(p)
			if self.mrm[1] < 2:
				self.sfrm(p,
				    ("inc", "dec")[self.mrm[1]],
				    ("Eb",), True)

		elif 0xff == iw:
			self.modRM(p)
			if self.mrm[1] == 0:
				self.sfrm(p, "inc", ("Ev",), True)
			elif self.mrm[1] == 1:
				self.sfrm(p, "dec", ("Ev",), True)
			elif self.mrm[1] == 2:
				self.mne = "call"
				self.o.append(self.ea(p))
				# XXX: can we do better ?
				self.flow = (("call", "T", None),)
			elif self.mrm[1] == 4:
				self.sfrm(p, "jmp", ("Ev",))
				if self.syntax == "att":
					self.o[0] = "*" + self.o[0]
				#self.mne = "JMP"
				#self.o.append(x[4])
				# XXX: can we do better ?
				self.flow = (("cond", "T", None),)
			elif self.mrm[1] == 6:
				self.sfrm(p, "push", ("Ev",), True)
	
		elif 0x0f01 == iw:
			self.osz = 16
			self.modRM(p)
			if self.mrm[1] == 2:
				self.sfrm(p, "lgdt", ("Ms",), True)
		elif 0x0f80 == iw & 0xfff0:
			#  ['JB', 'rel16off', '0F 82', 'cw', '\n']
			cx = self.cc[iw & 0xf]
			self.mne = "j" + cx
			if self.asz == 16:
				of = p.m.s16(self.na)
				self.na += 2
			elif self.asz == 32:
				of = p.m.s32(self.na)
				self.na += 4
			else:
				assert False
			da = self.na + of
			self.o.append("0x%04x" % da)
			self.flow = (
			    ('cond', cx, da),
			    ('cond', self.cc[(iw ^ 1) & 0xf], self.na)
			)
		elif 0x0fb6 == iw:
			self.modRM(p)
			if self.syntax == "intel":
				self.sfrm(p, "movzx", ("Gv", "Eb"))
			else:
				self.sfrm(p, "movzb", ("Gv", "Eb"), suff="*")
		elif 0x0fb7 == iw:
			self.modRM(p)
			if self.syntax == "intel":
				self.sfrm(p, "movzx", ("Gv", "Ew"))
			else:
				self.sfrm(p, "movzw", ("Gv", "Ew"), suff="*")
		elif 0x0fba == iw:
			self.modRM(p)
			if self.mrm[1] > 3:
				self.sfrm(p,
				    ("bt", "bts", "btr", "btc")[self.mrm[1]&3],
				    ("Ev", "Ib"))
			
		elif 0xdbe3 == iw:
			self.mne = "FNINIT"

		if self.mne == None:
			raise X86Error(self.ia, "No Disass ")
		if self.mne.lower() != self.mne:
			raise X86Error(self.ia,
			    "Old Style " + self.mne + " " + str(self.o))

	def disass(self, p, adr, priv = None):

		# Effective Operand Size
		self.osz = self.mosz

		# Effective Address Size
		self.asz = self.masz

		# Instruction Address
		self.ia = adr

		# Next Address
		self.na = adr

		# ModRM info
		self.mrm = None

		# SIP info
		self.sip = None

		# short info
		self.short = None

		# Operands
		self.o=list()

		# Destination Address
		self.da=None

		# Mnemonic
		self.mne =None

		# Flow information
		self.flow=None

		# Segment Prefix
		self.seg = ""

		try:
			self.__decode(p)
		except mem.MemError as foo:
			print("FAIL Bad location at 0x%x" % adr)
			return
		except X86Error as foo:
			print("FAIL x86 disassembly at 0x%x" % adr)
			print("	",foo)
			s = "\t"
			for i in range(0,15):
				try:
					s += "%02x " % p.m.rd(adr + i)
				except:
					s += "?? "
			print(s)
			self.unknown(p, adr)
			return

		if self.mne == None:
			print("NO x86 disassembly at 0x%x" % adr)
			return

		try:
			x = p.t.add(self.ia, self.na, "ins")
		except:
			return
		x.a['mne'] = self.mne
		x.a['oper'] = self.o
		if self.flow != None:
			x.a['flow'] = self.flow
		x.render = self.render
		p.ins(x, self.disass)

		try:
			self.verify(p,x)
		except:	
			print("(Verify failed)")

	def verify(self, p, x):

		from subprocess import check_output

		j=bytearray()
		for i in range(x.start,x.end):
			j.append(p.m.rd(i))

		f = open("/tmp/_x86.bin", "wb")
		f.write(j)
		f.close()
		r = check_output(
		    "objdump " +
		    "-b binary " +
		    "-D " +
		    "-mi386 " +
		    "-M" +
		    self.arch + 
		    "," + self.syntax +
		    " /tmp/_x86.bin", shell=True)
		r = r.decode('ascii').split("\n")
		r6 = r[6].split()
		r7 = r[7].split()
		s6 = "0:"
		s7 = "7:"
		for i in range(x.start, x.end):
			if i < x.start + 7:
				s6 += " %02x" % p.m.rd(i)
			else:
				s7 += " %02x" % p.m.rd(i)
		if x.end - x.start < 8:
			s7 = ""
		q =  x.render(p, x, 0)
		s6 += " " + q[0].expandtabs()
		s6 = s6.split()
		s7 = s7.split()
		if r6 == s6 and r7 == s7:
			return
		if r6[1] == '0f' and r6[2][0] == '8':
			return
		if r6[1] == 'e2':
			return
		if r6[1] == 'e9':
			return
		if r6[1] == 'e8':
			return
		if r6[1] == 'eb':
			return
		if r6[1][0] == '7':
			return
		print("--------------------------------------------------")
		print("MISMATCH 0x%x" % x.start)
		print("MRM: ", self.mrm)
		print("SIP: ", self.sip)
		print("SHORT: ", self.short)
		print("Should:")
		print(r6)
		print(r7)
		print("is:")
		print(s6)
		print(s7)
		print("--------------------------------------------------")

class x86_intel(x86):
	def __init__(self, mode):
		x86.__init__(self, mode)
		self.syntax = "intel"
		self.immpfx = ""

		self.reg8 = ( "al",  "cl",  "dl",  "bl",
		    "ah",  "ch",  "dh",  "bh")
		self.reg16 = ("ax",  "cx",  "dx",  "bx",
		     "sp",  "p",  "si",  "di")
		self.reg32 = ("eax", "ecx", "edx", "ebx",
		    "esp", "ebp", "esi", "edi")
		self.sReg = ( "es",  "cs",  "ss",  "ds",
		     "fs",  "gs",  None,   None)
		self.cReg = ( "cr0", "cr1", "cr2", "cr3",
		    "cr4", "cr5", "cr6", "cr7")
		self.mReg = "mm"
		self.dReg = "[dx]"
		self.xReg = { 16: "[si]", 32: "[esi]" }
		self.yReg = { 16: "[di]", 32: "[edi]" }

		self.gReg = { 8:  self.reg8, 16: self.reg16, 32: self.reg32, }

	def setargs(self, a, b):
		self.o.append(b)
		self.o.append(a)

	def sfrm(self, p, mne, args, suff=False, wid=0):
		self.short = (mne, args, suff, self.osz, self.asz)
		self.mne = mne

		if False and self.asz != self.masz:
			self.mne = "addr32 " + self.mne

		x = list(args)
		while len(x) < 2:
			x.append(None)
		src = x[0]
		dst = x[1]
		for i in x:
			self.fmarg(p, i)

	def ea(self, p, hint=None):
		if hint != None and hint[1] == 'b':
			mosz = 8
		elif hint != None and hint[1] == 'w':
			mosz = 16
		else:
			mosz = self.osz

		ea = self.seg
		l = None

		if self.mrm[0] == 3:
			ea = self.gReg[mosz][self.mrm[2]]
			return ea

		if self.asz == 16:
			if self.mrm[0] == 0 and self.mrm[2] == 6:
				x = p.m.s16(self.na)
				self.na += 2
				ea += "%d" % x
				return ea
			else:
				rx = "(" + self.modrm16[self.mrm[2]]
		elif self.asz == 32:
			if self.mrm[0] == 0 and self.mrm[2] == 5:
				v = p.m.w32(self.na)
				self.na += 4
				if self.seg == "":
					return "ds:0x%x" % v
				else:
					return self.seg + "0x%x" % v

			if self.mrm[2] == 4:
				sip = p.m.rd(self.na)
				self.na += 1
				sip_s = 1 << (sip >> 6)
				sip_i = (sip >> 3) & 7
				sip_b = sip & 7

				b=""
				r=""
				o=""
				if self.mrm[0] == 0 and sip_b == 5:
					w = p.m.s32(self.na)
					self.na += 4
					if w < 0:
						o = "%d" % w
					elif w > 0:
						o = "+%d" % w
				elif self.mrm[0] == 1 and sip_b == 5:
					#w = p.m.s8(self.na)
					#self.na += 1
					#if w < 0:
					#	o = "%d" % w
					#if w > 0:
					#	o = "+%d" % w
					b="ebp"
				elif self.mrm[0] == 2 and sip_b == 5:
					b="ebp"
					o = "+%d" % p.m.w32(self.na)
					self.na += 4
				else:
					b = self.reg32[sip_b]

				if sip_i != 4:
					r = self.reg32[sip_i]
					if sip_s != 1:
						r += "*%d" % sip_s

				self.sip = (sip_s, sip_i, sip_b, b,r,o)
				rx = b
				if r != "":
					if rx != "":
						rx += "+"
					rx += r
				if o != "":
					rx += o

			else:
				rx = self.reg32[self.mrm[2]]
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if self.mrm[0] == 0:
			f = None
		elif self.asz == 16 and self.mrm[0] == 1:
			x = p.m.s8(self.na)
			self.na += 1
			f = "%d"
		elif self.mrm[0] == 1:
			x = p.m.s8(self.na)
			self.na += 1
			if x < 0:
				rx += "%d" % x
			elif x > 0:
				rx += "+%d" % x
		elif self.mrm[0] == 2 and self.asz == 16:
			x = p.m.w16(self.na)
			self.na += 2
			f = "0x%04x"
		elif self.mrm[0] == 2 and self.asz == 32:
			x = p.m.s32(self.na)
			self.na += 4
			if x < 0:
				rx += "%d" % x
			elif x > 0:
				rx += "+%d" % x
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		ea = '[' + rx + ']'

		if hint == None:
			pass
		elif hint[1] == 'w':
			ea = "WORD PTR " + ea
		elif hint[1] == 'b':
			ea = "BYTE PTR " + ea
		elif hint[1] == 'v':
			if mosz == 16:
				ea = "WORD PTR " + ea
			elif mosz == 32:
				ea = "DWORD PTR " + ea

		if self.seg != "":
			ea = self.seg + ea
		return ea

	def imm(self, p, sz, se = False):
		#print("IMM", p, sz, se)
		if sz == 8:
			v = p.m.rd(self.na)
			if v & 0x80 and self.osz > 8:
				v |= 0xffffff00
			self.na += 1
		elif sz == 16:
			v = p.m.w16(self.na)
			self.na += 2
		elif sz == 32:
			v = p.m.w32(self.na)
			self.na += 4
		else:
			raise X86Error(self.na, "Wrong imm width (%d)" % sz)
		f = self.immpfx + "0x%x"
		return f % v

	def dir(self, p, sz):
		sg = self.seg
		if sg == "":
			sg = "ds:"
		if sz == 8:
			w =  p.m.rd(self.na)
			self.na += 1
			return (sg + "0x%x" % w, w)
		if sz == 16:
			w =  p.m.w16(self.na)
			self.na += 2
			return (sg + "0x%x" % w, w)
		if sz == 32:
			w =  p.m.w32(self.na)
			self.na += 4
			return (sg + "0x%x" % w, w)
		raise X86Error(self.na, "Wrong dir width (%d)" % sz)
