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

ins={ }

# Vol3 p364

reg8 = ( "%al",  "%cl",  "%dl",  "%bl",  "%ah",  "%ch",  "%dh",  "%bh")
reg16 = ("%ax",  "%cx",  "%dx",  "%bx",  "%sp",  "%bp",  "%si",  "%di")
reg32 = ("%eax", "%ecx", "%edx", "%ebx", "%esp", "%ebp", "%esi", "%edi")
sReg = ( "%es",  "%cs",  "%ss",  "%ds",  "%fs",  "%gs",  None,   None)
cReg = ( "%cr0", "%cr1", "%cr2", "%cr3", "%cr4", "%cr5", "%cr6", "%cr7")

gReg = {
	8:  reg8,
	16: reg16,
	32: reg32,
}

cc=("o", "no", "b", "nb", "z", "nz", "be", "nbe", 
    "s", "ns", "p", "np", "l", "nl", "le", "nle")

shifts=("rol", "shr", "shr", "shr", "shl", "shr", "sal", "sar")
alu=(   "add", "or",  "adc", "sbb", "and", "sub", "xor", "cmp")

modrm16 = ("%bx+%si", "%bx+%di", "%bp+%si", "%bp+%di",
	   "%si", "%di", "%bp", "%bx")

shortform = {
	# Args in same order as manual
	0x27:	("daa",		None,	None),
	0x60:	("pusha",	None,	None),
	0x61:	("popa",	None,	None),
	0x68:	("push",	"Iz",	None),
	0x6a:	("push",	"Ib",	None),
	0x6c:	("insb",	"Yb",	"DX"),
	0x6e:	("outsb",	"DX",	"Xb"),
	0x84:	("test",	"Eb",	"Gb"),
	0x85:	("test",	"Ev",	"Gv"),
	0x89:	("mov",		"Ev",	"Gv"),
	0x8a:	("mov",		"Gb",	"Eb"),
	0x8b:	("mov",		"Gv",	"Ev"),
	#XXX: objdump bug ?
	#0x8e:	("mov",		"Sw",	"Ew"),
	0x8e:	("mov",		"Sw",	"Ev"),
	0x90:	("nop",		None,	None),
	0x99:	("cltd",	None,	None),
	0xa0:	("mov",		"AL",	"Ob"),
	0xa9:	("test",	"rAX",	"Iz"),
	0xb0:	("mov",		"AL",	"Ib"),
	0xb3:	("mov",		"BL",	"Ib"),
	0xa1:	("mov", 	"AL", 	"Ob"),
	0xa1:	("mov", 	"rAX", 	"Ov"),
	0xa2:	("mov", 	"Ob", 	"AL"),
	0xa3:	("mov", 	"Ov", 	"rAX"),
	0xa8:	("test",	"AL",	"Ib"),
	0xaa:	("stos",	"Yb",	"AL"),
	0xab:	("stos",	"Yv",	"rAX"),
	0xb4:	("mov",		"AH",	"Ib"),
	0xc9:	("leave",	None,	None),
	0xcc:	("int3",	None,	None),
	0xe4:	("in",		"AL",	"Ib"),
	0xe5:	("in",		"eAX",	"Ib"),
	0xe6:	("out",		"Ib",	"AL"),
	0xe7:	("out",		"Ib",	"eAX"),
	0xec:	("in",		"AL",	"DX"),
	0xed:	("in",		"eAX",	"DX"),
	0xee:	("out",		"DX",	"AL"),
	0xef:	("out",		"DX",	"eAX"),
	0xf3:	("repz",	None,	None),
	0xf8:	("clc",		None,	None),
	0xfa:	("cli",		None,	None),
	0xfb:	("sti",		None,	None),
	0xfc:	("cld",		None,	None),
	0x0f08:	("invd",	None,	None),
	0x0f09:	("wbinvd",	None,	None),
	0x0f20:	("mov",		"Rd/q",	"Cd/q"),
	0x0f22:	("mov",		"Cd/q",	"Rd/q"),
	0x0f30:	("wrmsr",	None,	None),
	0x0f32:	("rdmsr",	None,	None),
	0x0f6e: ("movd",	"Pq",	"Ed/q"),
	0x0f77:	("emms",	None,	None),
	0x0f94:	("sete",	"Eb",	None),
	0x0f95:	("setne",	"Eb",	None),
	0x0fa2:	("cpuid",	None,	None),
	0x0faf:	("imul",	"Gv",	"Ev"),
	0x0fb6:	("movzbl",	"Gv",	"Eb"),
	0x0fb7:	("movzwl",	"Gv",	"Ew"),
	0x0fbc:	("bsf",		"Gv",	"Ev"),
}

class x86(object):
	def __init__(self, mode):
		self.setmode(mode)

	def setmode(self, mode):
		if mode == "real":
			self.mosz=16
			self.masz=16
			self.arch="i8086"
		elif mode == "32bit":
			self.mosz=32
			self.masz=32
			self.arch="i385"
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

	# Return:
	#	x[0] = mod
	#	x[1] = reg
	#	x[2] = rm
	#	x[3] = oper
	#
	def modRM(self, p, osz, asz):
		if self.mrm != None:
			return self.mrm

		modrm = p.m.rd(self.na)
		self.na += 1
		mod = modrm >> 6
		reg = (modrm >> 3) & 7
		rm = modrm & 7
		ea = self.seg
		l = None

		if mod == 3:
			ea = gReg[osz][rm]
			self.mrm = (mod, reg, rm, ea)
			return

		if asz == 16:
			if mod == 0 and rm == 6:
				x = p.m.s16(self.na + l)
				l += 2
				ea += "(0x%04x)" % x
				self.mrm = (mod, reg, rm, ea)
				return
			else:
				rx = "(" + modrm16[rm]
		elif asz == 32:
			if rm == 4:
				sip = p.m.rd(self.na)
				self.na += 1
				sip_s = 1 << (sip >> 6)
				sip_i = (sip >> 3) & 7
				sip_b = sip & 7
				if mod == 0 and sip_b == 5:
					rx = "0x%x(" % p.m.w32(self.na)
					self.na += 4
				else:
					rx = "(" + reg32[sip_b]
				if sip_i != 4:
					rx += "," + reg32[sip_i]
					rx += ",%d" % sip_s
			elif mod == 0 and rm == 5:
				rx = "0x%x" % p.m.w32(self.na)
				self.na += 4
			else:
				rx = "(" + reg32[rm]
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if mod == 0:
			ea = self.seg + rx
			f = None
		elif mod == 1:
			x = p.m.rd(self.na)
			if x & 0x80:
				x |= 0xffffff00
			self.na += 1
			f = "0x%02x"
		elif mod == 2 and asz == 16:
			x = p.m.s16(self.na)
			self.na += 2
			f = "0x%04x"
		elif mod == 2 and asz == 32:
			x = p.m.s32(self.na)
			self.na += 4
			f = "0x%08x"
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if False:
			if x < 0:
				ea += rx + "-" + f % (-x)
			else:
				ea += rx + "+" + f % x
		elif f != None:
			f = "0x%x"
			ea = f % x + rx
		if ea.find("(") > -1:
			ea += ")"
		self.mrm = (mod, reg, rm, ea)
		return

	# Return:
	#	x[0] = len
	#	x[1] = oper
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

	# Return:
	#	x[0] = len
	#	x[1] = oper
	def imm(self, p, sz, se = False):
		#print("IMM", p, sz, se)
		if sz == 8:
			f = "$0x%02x"
			v = p.m.rd(self.na)
			if v & 0x80 and se:
				v |= 0xffffff00
			self.na += 1
		elif sz == 16:
			f = "$0x%04x"
			v = p.m.w16(self.na)
			self.na += 2
		elif sz == 32:
			f = "$0x%08x"
			v = p.m.w32(self.na)
			self.na += 4
		else:
			raise X86Error(self.na, "Wrong imm width (%d)" % sz)
		f = "$0x%x"
		return f % v

	def __short(self, p, mne, dst, src = None, suff=False):
		self.short = (mne, dst, src, suff)
		self.mne = mne
		for i in (src, dst):
			if i == None:
				pass
			elif i == "AL":
				self.o.append("%al")
			elif i == "AH":
				self.o.append("%ah")
			elif i == "BL":
				self.o.append("%bl")
			elif i == "eAX":
				# XXX: is this a type for rAX ?
				self.o.append(gReg[self.osz][0])
			elif i == "rAX":
				self.o.append(gReg[self.osz][0])
			elif i == "CL":
				self.o.append("%cl")
			elif i == "DX":
				self.o.append("(%dx)")
			elif i == "Ib":
				if dst == "Eb" or self.mrm == None:
					self.o.append(self.imm(p, 8))
				else:
					self.o.append(self.imm(p, 8, True))
			elif i == "Iz":
				self.o.append(self.imm(p, self.osz))
			elif i == "Gv":
				self.modRM(p, self.osz, self.asz)
				self.o.append(gReg[self.osz][self.mrm[1]])
			elif i == "Gb":
				self.modRM(p, 8, self.asz)
				self.o.append(gReg[8][self.mrm[1]])
			elif i == "Eb":
				self.modRM(p, 8, self.asz)
				self.o.append(self.mrm[3])
			elif i == "Ev":
				self.modRM(p, self.osz, self.asz)
				self.o.append(self.mrm[3])
			elif i == "Ew":
				self.modRM(p, 16, self.asz)
				self.o.append(self.mrm[3])
			elif i == "Ed/q":
				self.modRM(p, 32, self.asz)
				self.o.append(self.mrm[3])
			elif i == "Cd/q":
				self.modRM(p, 32, self.asz)
				self.o.append("%cr" + "%d" % self.mrm[1])
			elif i == "Rd/q":
				self.modRM(p, 32, self.asz)
				if self.mrm[0] != 3:
					raise X86Error(self.ia, "Rd/q mod!=3")
				self.o.append(gReg[32][self.mrm[2]])
			elif i == "Ob":
				x = self.dir(p, self.asz)
				self.o.append(x[0])
			elif i == "Ov":
				x = self.dir(p, self.asz)
				self.o.append(x[0])
			elif i == "Pq":
				self.o.append("%mm" + "%d" % self.mrm[1])
			elif i == "Sw":
				self.o.append(sReg[self.mrm[1]])
			elif i == "Xb":
				self.o.append("%ds:(%esi)")
			elif i == "Yb":
				self.o.append("%es:(%edi)")
			elif i == "Yv":
				self.o.append("%es:(%edi)")
			else:
				raise X86Error(self.ia,
				    "Unknown short (%s)" % i)
		# Suffix Rules
		if suff and src == "Ib" and dst == "Ev" and self.mrm[0] != 3:
			if self.osz == 32:
				self.mne += "l"
			else:
				self.mne += "w"
		if suff and src == "Iz" and dst == "Ev" and self.mrm[0] != 3:
			if self.osz == 32:
				self.mne += "l"
			else:
				self.mne += "w"
		if suff and src == None and dst == "Ev" and self.mrm[0] != 3:
			if self.osz == 32:
				self.mne += "l"
			else:
				self.mne += "w"
		if suff and src == "Ib" and dst == "Eb" and self.mrm[0] != 3:
			self.mne += "b"
		if suff and src == None and dst == "Eb" and self.mrm[0] != 3:
			self.mne += "b"

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
				self.seg = "%es:"
			elif iw == 0x2e:
				self.seg = "%cs:"
			elif iw == 0x3e:
				self.seg = "%ds:"
			elif iw == 0x64:
				self.seg = "%fs:"
			elif iw == 0x65:
				self.seg = "%gs:"
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
			self.__short(p, ss[0], ss[1], ss[2])
		elif 0x00 == iw & 0xffcc:
			self.__short(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    ("Eb",  "Ev",  "Gb",  "Gv" )[iw & 3],
			    ("Gb",  "Gv",  "Eb",  "Ev" )[iw & 3])
		elif 0x04 == iw & 0xffcf:
			self.__short(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    "AL", "Ib")
		elif 0x05 == iw & 0xffcf:
			self.__short(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    "rAX", "Iz")
		elif 0x06 == iw:
			#  ['PUSH', 'ES', '06', '', '\n']
			self.mne ="PUSH"
			self.o.append("%es")
		elif 0x07 == iw:
			#  ['POP', 'ES', '07', '', '\n']
			self.mne ="POP"
			self.o.append("%es")
		elif 0x08 == iw & 0xffcc:
			self.__short(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    ("Eb",  "Ev",  "Gb",  "Gv" )[iw & 3],
			    ("Gb",  "Gv",  "Eb",  "Ev" )[iw & 3])
		elif 0x0c == iw & 0xffcf:
			self.__short(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    "AL", "Ib")
		elif 0x0d == iw & 0xffcf:
			self.__short(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    "rAX", "Iz")
		elif 0x0e == iw:
			self.mne ="PUSH"
			self.o.append("%cs")
		elif 0x16 == iw:
			self.mne ="PUSH"
			self.o.append("%ss")
		elif 0x1E == iw:
			self.mne ="PUSH"
			self.o.append("%ds")
		elif 0x1F == iw:
			self.mne ="POP"
			self.o.append("%ds")
		elif 0x40 == iw & 0xfff8:
			self.mne ="inc"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x48 == iw & 0xfff8:
			self.mne ="dec"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x50 == iw & 0xfff8:
			self.mne ="push"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x58 == iw & 0xfff8:
			self.mne ="pop"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x69 == iw:
			self.__short(p, "imul", "Gv", "Ev")
			self.o.insert(0, self.imm(p, self.osz))
		elif 0x6b == iw:
			self.__short(p, "imul", "Gv", "Ev")
			self.o.insert(0, self.imm(p, 8))
		elif 0x70 == iw & 0xfff0:
			#  ['Jcc', 'rel8off', '75', 'cb', '\n']
			cx = cc[iw & 0xf]
			self.mne = "j" + cx
			da = self.ia + 2 + p.m.s8(self.ia + 1)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow = (
			    ('cond', cx, da),
			    ('cond', cc[(iw ^ 1) & 0xf], self.ia + 2)
			)
		elif 0x80 == iw:
			self.modRM(p, 8, self.asz)
			self.__short(p, alu[self.mrm[1]], "Eb", "Ib", True)
		elif 0x81 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, alu[self.mrm[1]], "Ev", "Iz", True)
		elif 0x83 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, alu[self.mrm[1]], "Ev", "Ib", True)
		elif 0x86 == iw:
			#  ['XCHG', 'reg/mem8 reg8', '86', '/r', '\n']
			self.mne = "XCHG"
			x = self.modRM(p, 8, self.asz)
			self.o.append(reg8[x[2]])
			self.o.append(x[4])
		elif 0x87 == iw:
			#  ['XCHG', 'reg/mem16 reg16', '87', '/r', '\n']
			self.mne = "XCHG"
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(gReg[self.osz][x[2]])
			self.o.append(x[4])
		elif 0x88 == iw:
			self.__short(p, "mov", "Eb", "Gb")
			if False:
				#  ['MOV', 'reg/mem8 reg8', '88', '/r', '\n']
				self.mne = "MOV"
				x = self.modRM(p, 8, self.asz)
				self.o.append(x[4])
				self.o.append(reg8[x[2]])
		elif 0x8c == iw:
			#  ['MOV', 'reg16/32/64/mem16 segReg', '8C', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(x[4])
			self.o.append(sReg[x[2]])
		elif 0x8d == iw:
			#  ['LEA', 'reg16 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg32 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg64 mem', '8D', '/r', '\n']
			self.mne = "lea"
			# XXX: osz or asz ?? 
			self.modRM(p, self.osz, self.asz)
			self.o.append(self.mrm[3])
			self.o.append(gReg[self.osz][self.mrm[1]])
		elif 0x8f == iw:
			x = self.modRM(p, self.osz, self.asz)
			if x[2] == 0:
				self.mne = "POP"
				self.o.append(x[4])
		elif 0x9b == iw:
			self.mne = "FWAIT"
		elif 0xb8 == iw & 0xfff8:
			#  ['MOV', 'reg16 imm16', 'B0', '+rw iw', '\n']
			#  ['MOV', 'reg32 imm32', 'B0', '+rd id', '\n']
			#  ['MOV', 'reg64 imm64', 'B0', '+rq iq', '\n']
			self.mne ="mov"
			self.o.append(self.imm(p, self.osz))
			self.o.append(gReg[self.osz][iw & 7])
		elif 0xc0 == iw:
			self.modRM(p, 8, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Eb", "Ib")
		elif 0xc1 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Ev", "Ib")
		elif 0xc3 == iw:
			#  ['RET', '', 'E3', '', '\n']
			self.mne ="ret"
			self.flow = (('ret', 'T', None),)
		elif 0xc6 == iw:
			self.modRM(p, 8, self.asz)
			if self.mrm[1] == 0:
				self.__short(p, 'mov', 'Eb', 'Ib', True)
		elif 0xc7 == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[1] == 0:
				self.__short(p, 'mov', 'Ev', 'Iz', True)
		elif 0xc8 == iw:
			#  ['ENTER', 'imm16 0', 'C8', 'iw 00', '\n']
			#  ['ENTER', 'imm16 1', 'C8', 'iw 01', '\n']
			#  ['ENTER', 'imm16 imm8', 'C8', '', '\n']
			self.mne ="ENTER"
			self.o.append(self.imm(p, 16))
			self.o.append(self.imm(p, 8))
		elif 0xcd == iw:
			#  ['INT', 'imm8', 'CD', 'ib', '\n']
			self.mne ="INT"
			self.o.append(self.imm(p, 8))
			self.flow = (('call', 'T', None),)
		elif 0xcf == iw:
			self.mne ="IRET"
			self.flow = (('ret', 'T', None),)
		elif 0xd0 == iw:
			self.modRM(p, 8, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Eb")
		elif 0xd1 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Ev")
		elif 0xd2 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Eb", "CL")
		elif 0xd3 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, shifts[self.mrm[1]], "Ev", "CL")
		elif 0xd9 == iw:
			# FP
			self.modRM(p, self.osz, self.asz)
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
			self.mne ="JMP"
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
			self.o.append("FAR")
			self.o.append("0x%04x" % sg)
			self.o.append(fx % off)
			if self.mode == "real":
				self.flow=(('cond', 'T', (sg << 4) + off),)
			else:
				assert False
		elif 0xeb == iw:
			#  ['JMP', 'rel8off', 'EB', 'cb', '\n']
			self.mne = "jmp"
			da = self.ia + 2 + p.m.s8(self.na)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow=(('cond', 'T', da),)
		elif 0xf4 == iw:
			#  ['HLT', '', 'E3', '', '\n']
			self.mne ="HLT"
			self.flow = (('halt', 'T', None),)
		elif 0xf6 == iw:
			#  ['TEST', 'reg/mem8 imm8', 'F6', '/0 ib', '\n']
			# &c
			self.modRM(p, 8, self.asz)
			if self.mrm[1] < 2:
				self.__short(p, "test", "Eb", "Ib", True)

		elif 0xf7 == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[1] < 2:
				self.__short(p, "test", "Ev", "Iz", True)
			else:
				self.__short(p,
				    ("", "", "not", "neg", "mul", "imul",
				    "div", "idiv")[self.mrm[1]],
				    "Ev", None, True)
		elif 0xfe == iw:
			self.modRM(p, 8, self.asz)
			if self.mrm[1] < 2:
				self.__short(p,
				    ("inc", "dec")[self.mrm[1]],
				    "Eb", None, True)

		elif 0xff == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[1] == 0:
				self.__short(p, "incl", "Ev")
			elif self.mrm[1] == 1:
				self.__short(p, "decl", "Ev")
			elif self.mrm[1] == 2:
				self.mne = "CALL"
				self.o.append(x[4])
				# XXX: can we do better ?
				self.flow = (("call", "T", None),)
			elif self.mrm[1] == 4:
				self.__short(p, "jmp", "Ev")
				self.o[0] = "*" + self.o[0]
				#self.mne = "JMP"
				#self.o.append(x[4])
				# XXX: can we do better ?
				self.flow = (("cond", "T", None),)
			elif self.mrm[1] == 6:
				self.__short(p, "pushl", "Ev")
	
		elif 0x0f01 == iw:
			x = self.modRM(p, 16, self.asz)
			if x[2] == 2:
				self.mne ="LGDT"
				self.o.append(x[4])
		elif 0x0f80 == iw & 0xfff0:
			#  ['JB', 'rel16off', '0F 82', 'cw', '\n']
			cx = cc[iw & 0xf]
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
			    ('cond', cc[(iw ^ 1) & 0xf], self.na)
			)
		elif 0x0fac == iw:
			self.__short(p, "shrd", "Ev", "Gv")
			self.o.insert(0, self.imm(p, 8))
		elif 0x0fba == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[1] > 3:
				self.__short(p,
				    ("bt", "bts", "btr", "btc")[self.mrm[1]&3],
				    "Ev", "Ib")
			
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

		self.verify(p,x)

	def verify(self, p, x):

		from subprocess import check_output

		j=bytearray()
		for i in range(x.start,x.end):
			j.append(p.m.rd(i))

		f = open("/tmp/_x86.bin", "wb")
		f.write(j)
		f.close()
		r = check_output("objdump -b binary -D -mi386 -M" + self.arch +
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
		print("SHORT: ", self.short)
		print("Should:")
		print(r6)
		print(r7)
		print("is:")
		print(s6)
		print(s7)
		print("--------------------------------------------------")
