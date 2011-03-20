#!/usr/local/bin/python
#
# Intel x86 family CPU disassembler
#

from __future__ import print_function

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

shifts=("rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar")
alu=(   "add", "or",  "adc", "sbb", "and", "sub", "xor", "cmp")

modrm16 = ("%bx+%si", "%bx+%di", "%bp+%si", "%bp+%di",
	   "%si", "%di", "%bp", "%bx")

shortform = {
	0x68:	("push",	"Iz",	None),
	0x6a:	("push",	"Ib",	None),
	0x85:	("test",	"Ev",	"Gv"),
	0x89:	("mov",		"Ev",	"Gv"),
	0x8b:	("mov",		"Gv",	"Ev"),
	0xb0:	("mov",		"AL",	"Ib"),
	0xa2:	("mov", 	"Ob",	"AL"),
	0xc9:	("leave",	None,	None),
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
				d = ', '
		return (s,)

	def unknown(self, p, adr, adr2 = None):
		from subprocess import call

		if adr2 == None:
			adr2 = adr
		j=bytearray()
		for i in range(0,15):
			j.append(p.m.rd(self.ia + i))

		f = open("/tmp/_x86.bin", "wb")
		f.write(j)
		f.close()
		print("--------------------------------------------------")
		call("objdump -b binary -D -mi386 -M" + self.arch +
		    " /tmp/_x86.bin", shell=True)
		print("--------------------------------------------------")

	# Return:
	#	x[0] = len
	#	x[1] = mod
	#	x[2] = reg
	#	x[3] = rm
	#	x[4] = oper
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
			self.mrm = (l, mod, reg, rm, ea)
			return self.mrm

		if asz == 16:
			if mod == 0 and rm == 6:
				x = p.m.s16(self.na + l)
				l += 2
				ea += "(0x%04x)" % x
				self.mrm = (l, mod, reg, rm, ea)
				return self.mrm
			else:
				rx = modrm16[rm]
		elif asz == 32:
			if rm == 4:
				sip = p.m.rd(self.na)
				self.na += 1
				sip_s = 1 << (sip >> 6)
				sip_i = (sip >> 3) & 7
				sip_b = sip & 7
				if sip_i != 4:
					rx = reg32[sip_i] + "+"
					if sip_s > 1:
						rx += "*%d+" % sip_s
				else:
					rx = ""
				if sip_b != 5:
					rx += reg32[sip_b]
				else:
					raise X86Error(self.ia,
					    "Unhandled 32bit ModRM (rIP)")
				print("RX= <%s>" % rx)
			elif mod == 0 and rm == 5:
				raise X86Error(self.ia,
				    "Unhandled 32bit ModRM (rIP)")
			else:
				rx = reg32[rm]
		else:
			raise X86Error(self.ia, "Unhandled 32bit ModRM")

		if mod == 0:
			ea = self.seg + "(" + rx + ")"
			self.mrm = (l, mod, reg, rm, ea)
			return self.mrm

		if mod == 1:
			x = p.m.s8(self.na)
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

		if x < 0:
			ea += "(" + rx + "-" + f % (-x) + ")" 
		else:
			ea += "(" + rx + "+" + f % x + ")" 
		self.mrm = (l, mod, reg, rm, ea)
		return self.mrm

	# Return:
	#	x[0] = len
	#	x[1] = oper
	def dir(self, p, sz):
		if sz == 8:
			w =  p.m.rd(self.na)
			self.na += 1
			return ("0x%02x" % w, w)
		if sz == 16:
			w =  p.m.w16(self.na)
			self.na += 2
			return ("0x%04x" % w, w)
		if sz == 32:
			w =  p.m.w32(self.na)
			self.na += 4
			return ("0x%08x" % w, w)
		raise X86Error(self.na, "Wrong dir width (%d)" % sz)

	# Return:
	#	x[0] = len
	#	x[1] = oper
	def imm(self, p, sz):
		if sz == 8:
			f = "$0x%02x"
			v = p.m.rd(self.na)
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
		return f % v

	def __short(self, p, mne, dst, src = None):
		self.mne = mne
		for i in (dst, src):
			if i == None:
				pass
			elif i == "AL":
				self.o.append("%al")
			elif i == "Ib":
				self.o.append(self.imm(p, 8))
			elif i == "Iz":
				self.o.append(self.imm(p, self.osz))
			elif i == "Ev":
				mrm = self.modRM(p, self.osz, self.asz)
				self.o.append(gReg[self.osz][mrm[2]])
			elif i == "Gv":
				mrm = self.modRM(p, self.osz, self.asz)
				self.o.append(mrm[4])
			elif i == "Ob":
				x = self.dir(p, self.asz)
				self.o.append(x[0])
			else:
				raise X86Error(self.ia,
				    "Unknown short (%s)" % i)

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
			self.ia += 1
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
		elif 0x00 == iw & 0xffcf:
			#  ['ADD', 'reg/mem8 reg8', '00', '/r', '\n']
			self.mne =("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, 8, self.asz)
			self.o.append(reg8[x[2]])
			self.o.append(x[4])
		elif 0x01 == iw & 0xffcf:
			self.__short(p, 
			    ("add", "adc", "and", "xor")[(iw>>4) & 3],
			    "Ev", "Gv")
		elif 0x02 == iw & 0xffcf:
			#  ['XOR', 'reg8 reg/mem8', '32', '/r the', '\n']
			self.mne =("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, 8, self.asz)
			self.o.append(x[4])
			self.o.append(reg8[x[2]])
		elif 0x03 == iw & 0xffcf:
			#  ['ADD', 'reg16 reg/mem16', '03', '/r', '\n']
			#  etc
			self.mne =("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(gReg[self.osz][x[2]])
			self.o.append(x[4])
		elif 0x04 == iw & 0xffcf:
			#  ['ADD', 'reg16 reg/mem16', '03', '/r', '\n']
			#  etc
			self.mne =("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			self.o.append("%al")
			self.o.append(self.imm(p, 8))
		elif 0x05 == iw & 0xffcf:
			#  ['ADD', 'AX imm16', '25', 'iw', '\n']
			#  ['ADD', 'EAX imm32', '25', 'id', '\n']
			#  ['ADD', 'RAX imm32', '25', 'id', '\n']
			#  &c
			self.mne =("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			self.o.append(gReg[self.osz][0])
			self.o.append(self.imm(p, self.osz))
		elif 0x06 == iw:
			#  ['PUSH', 'ES', '06', '', '\n']
			self.mne ="PUSH"
			self.o.append("%es")
		elif 0x07 == iw:
			#  ['POP', 'ES', '07', '', '\n']
			self.mne ="POP"
			self.o.append("%es")
		elif 0x08 == iw & 0xffcf:
			#  ['CMP', 'reg/mem8 reg8', '38', '/r', '\n']
			self.mne =("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			x = self.modRM(p, 8, self.asz)
			self.o.append(reg8[x[2]])
			self.o.append(x[4])
		elif 0x09 == iw & 0xffcf:
			self.__short(p, 
			    ("or", "sbb", "sub", "cmp")[(iw>>4) & 3],
			    "Ev", "Gv")
		elif 0x0a == iw & 0xffcf:
			#  ['OR', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['SBB', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['SUB', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['CMP', 'reg8 reg/mem8', '2A', '/r', '\n']
			self.mne =("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			x = self.modRM(p, 8, self.asz)
			self.o.append(reg8[x[2]])
			self.o.append(x[4])
		elif 0x0b == iw & 0xffcf:
			#  ['OR', 'reg16 reg/mem16', '2B', '/r', '\n']
			#  ['OR', 'reg32 reg/mem32', '2B', '/r', '\n']
			#  ['OR', 'reg64 reg/mem64', '2B', '/r', '\n']
			#  &c
			self.mne =("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			self.mne = "SUB"
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(gReg[self.osz][x[2]])
			self.o.append(x[4])
		elif 0x0c == iw & 0xffcf:
			#  ['OR', 'AL imm8', '0C', 'ib', '\n']
			self.mne =("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			self.o.append("%al")
			self.o.append(self.imm(p, 8))
		elif 0x0d == iw & 0xffcf:
			#  ['OR', 'AX imm16', '0D', 'iw', '\n']
			#  ['OR', 'EAX imm32', '0D', 'id', '\n']
			#  ['OR', 'RAX imm32', '0D', 'id', '\n']
			#  &c
			self.mne =("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			self.o.append(gReg[self.osz][0])
			self.o.append(self.imm(p, self.osz))
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
			self.mne ="DEC"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x50 == iw & 0xfff8:
			self.mne ="push"
			self.o.append(gReg[self.osz][iw & 0x07])
		elif 0x58 == iw & 0xfff8:
			self.mne ="pop"
			self.o.append(gReg[self.osz][iw & 0x07])
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
			#  ['ADC', 'reg/mem8 imm8', '80', '/2 ib', '\n']
			#  ['ADD', 'reg/mem8 imm8', '80', '/0 ib', '\n']
			#  ['AND', 'reg/mem8 imm8', '80', '/4 ib', '\n']
			#  ['CMP', 'reg/mem8 imm8', '80', '/7 ib', '\n']
			#  ['OR', 'reg/mem8 imm8', '80', '/1 ib', '\n']
			#  ['SBB', 'reg/mem8 imm8', '80', '/3 ib', '\n']
			#  ['SUB', 'reg/mem8 imm8', '80', '/5 ib', '\n']
			#  ['XOR', 'reg/mem8 imm8', '80', '/6 ib', '\n']
			x = self.modRM(p, 8, self.asz)
			self.mne = alu[x[2]]
			self.o.append(x[4])
			self.o.append(self.imm(p, 8))

		elif 0x81 == iw:
			#  ['ADC', 'reg/mem16 imm16', '81', '/2 iw', '\n']
			#  ['ADC', 'reg/mem32 imm32', '81', '/2 id', '\n']
			#  ['ADC', 'reg/mem64 imm32', '81', '/2 id', '\n']
			#  &c
			x = self.modRM(p, self.osz, self.asz)
			self.mne = alu[x[2]]
			self.o.append(x[4])
			self.o.append(self.imm(p, self.osz))
		elif 0x83 == iw:
			#  ['ADC', 'reg/mem16 imm8', '83', '/2 ib', '\n']
			#  ['ADC', 'reg/mem32 imm8', '83', '/2 ib', '\n']
			#  ['ADC', 'reg/mem64 imm8', '83', '/2 ib', '\n']
			#  &c
			x = self.modRM(p, self.osz, self.asz)
			self.mne = alu[x[2]]
			self.o.append(self.imm(p, 8))
			self.o.append(x[4])
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
			#  ['MOV', 'reg/mem8 reg8', '88', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, 8, self.asz)
			self.o.append(x[4])
			self.o.append(reg8[x[2]])
		elif 0x8a == iw:
			# ['MOV', 'reg8 reg/mem8', '8A', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, 8, self.asz)
			self.o.append(reg8[x[2]])
			self.o.append(x[4])
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
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(gReg[self.osz][x[2]])
			self.o.append(x[4])
		elif 0x8e == iw:
			#  ['MOV', 'segReg reg/mem16', '8E', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, self.osz, self.asz)
			self.o.append(sReg[x[2]])
			self.o.append(x[4])
		elif 0x8f == iw:
			x = self.modRM(p, self.osz, self.asz)
			if x[2] == 0:
				self.mne = "POP"
				self.o.append(x[4])
			else:
				self.unknown(p, adr, self.ia)
				return
		elif 0x90 == iw & 0xfff8:
			self.mne = "XCHG"
			assert(self.osz == 16)
			self.o.append("%ax")
			self.o.append(gReg[self.osz][iw & 7])
		elif 0x9b == iw:
			self.mne = "FWAIT"
		elif 0xa0 == iw:
			#  ['MOV', 'AL moffset8', 'A0', '', '\n']
			self.mne ="MOV"
			x = self.dir(p, self.asz)
			self.o.append("%al")
			self.o.append(x[0])
		elif 0xa1 == iw:
			#  ['MOV', 'AX moffset16', 'A1', '', '\n']
			#  ['MOV', 'AX moffset32', 'A1', '', '\n']
			#  ['MOV', 'AX moffset64', 'A1', '', '\n']
			self.mne ="MOV"
			x = self.dir(p, self.asz)
			self.o.append(x[0])
			self.o.append(gReg[self.osz][0])
		elif 0xa3 == iw:
			#  ['MOV', 'moffset16 AX', 'A3', '', '\n']
			self.mne ="MOV"
			self.o.append(gReg[self.osz][0])
			x = self.dir(p, self.asz)
			self.o.append(x[0])
		elif 0xa8 == iw:
			#  ['ADD', 'reg/mem8 reg8', '00', '/r', '\n']
			self.mne ="TEST"
			self.o.append("%al")
			self.o.append(self.imm(p, 8))
		elif 0xa9 == iw:
			#  ['TEST', 'AX imm16', 'A9', 'iw', '\n']
			#  ['TEST', 'EAX imm32', 'A9', 'id', '\n']
			#  ['TEST', 'RAX imm32', 'A9', 'id', '\n']
			self.mne ="TEST"
			self.o.append(gReg[self.osz][0])
			self.o.append(self.imm(p, self.osz))
		elif 0xb8 == iw & 0xfff8:
			#  ['MOV', 'reg16 imm16', 'B0', '+rw iw', '\n']
			#  ['MOV', 'reg32 imm32', 'B0', '+rd id', '\n']
			#  ['MOV', 'reg64 imm64', 'B0', '+rq iq', '\n']
			self.mne ="mov"
			self.o.append(gReg[self.osz][iw & 7])
			self.o.append(self.imm(p, self.osz))
		elif 0xc0 == iw:
			self.modRM(p, 8, self.asz)
			self.__short(p, shifts[self.mrm[2]], "Eb", "Ib")
		elif 0xc1 == iw:
			self.modRM(p, self.osz, self.asz)
			self.__short(p, shifts[self.mrm[2]], "Ev", "Ib")
		elif 0xc3 == iw:
			#  ['RET', '', 'E3', '', '\n']
			self.mne ="ret"
			self.flow = (('ret', 'T', None),)
		elif 0xc6 == iw:
			self.modRM(p, 8, self.asz)
			if self.mrm[2] == 0:
				self.__short('mov', 'Eb', 'Ib')
		elif 0xc7 == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[2] == 0:
				self.__short(p, 'mov', 'Ev', 'Iz')
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
			#  ['ROL', 'reg/mem8 1', 'D0', '/0', '\n']
			#  &c
			x = self.modRM(p, 8, self.asz)
			self.mne = shifts[x[2]]
			self.o.append(x[4])
		elif 0xd1 == iw:
			#  ['RCL', 'reg/mem16 1', 'D1', '/2', '\n']
			#  &c
			x = self.modRM(p, self.osz, self.asz)
			self.mne = shifts[x[2]]
			self.o.append(x[4])
		elif 0xd2 == iw:
			#  ['RCL', 'reg/mem8 CL', 'D2', '/2 bit', '\n']
			#  &c
			x = self.modRM(p, 8, self.asz)
			self.mne = shifts[x[2]]
			self.o.append(x[4])
			self.o.append("%cl")
		elif 0xd3 == iw:
			#  ['RCL', 'reg/mem16 CL', 'D3', '/2 bit', '\n']
			#  &c
			x = self.modRM(p, self.osz, self.asz)
			self.mne = shifts[x[2]]
			self.o.append(x[4])
			self.o.append("%cl")
		elif 0xd9 == iw:
			# FP
			x = self.modRM(p, self.osz, self.asz)
			if x[1] != 3 and x[3] == 6:
				self.na += 1
				self.mne ="FNSTCW"
				self.o.append(self.imm(p, 16))
			else:
					
				print(x)
				self.unknown(p, adr, self.ia)
				return
		elif 0xe0 == iw & 0xfffc:
			#  ['LOOP', 'rel8off', 'E2', 'cb', '\n']
			self.mne = ("LOOPNE", "LOOPE", "LOOP", "JCXZ")[iw & 3]
			da = self.ia + 2 + p.m.s8(self.ia + 1)
			self.na += 1
			self.o.append("0x%x" % da)
			self.flow = (
			    ('cond', "XXX1", da),
			    ('cond', "XXX2",  self.na)
			)
		elif 0xe4 == iw:
			#  ['IN', 'AL imm8 ', 'E4', 'ib', '\n']
			self.mne ="OUT"
			self.o.append("%al")
			self.o.append("#0x%02x" % p.m.rd(self.na))
			self.na += 1
		elif 0xe6 == iw:
			#  ['OUT', 'imm8 AL', 'E6', 'ib', '\n']
			self.mne ="OUT"
			self.o.append("#0x%02x" % p.m.rd(self.na))
			self.na += 1
			self.o.append("%al")
		elif 0xe7 == iw:
			#  ['OUT', 'imm8 AX', 'E7', 'ib', '\n']
			#  ['OUT', 'imm8 EAX', 'E7', 'ib', '\n']
			self.mne ="OUT"
			self.o.append("#0x%02x" % p.m.rd(self.na))
			self.na += 1
			self.o.append(gReg[self.osz][0])
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
		elif 0xec == iw:
			#  ['IN', 'AL DX', 'EC', '', '\n']
			self.mne ="IN"
			self.o.append("%al")
			self.o.append("(%dx)")
		elif 0xed == iw:
			#  ['IN', 'AX DX', 'ED', '', '\n']
			#  ['IN', 'EAX DX', 'ED', '', '\n']
			self.mne ="IN"
			self.o.append(gReg[self.osz][0])
			self.o.append("(%dx)")
		elif 0xee == iw:
			#  ['OUT', 'DX AL ', 'EE', '', '\n']
			self.mne ="OUT"
			self.o.append("(%dx)")
			self.o.append("%al")
		elif 0xef == iw:
			#  ['OUT', 'DX AX ', 'EF', '', '\n']
			#  ['OUT', 'DX EAX ', 'EF', '', '\n']
			self.mne ="OUT"
			self.o.append("(%dx)")
			self.o.append(gReg[self.osz][0])
		elif 0xf4 == iw:
			#  ['HLT', '', 'E3', '', '\n']
			self.mne ="HLT"
			self.flow = (('halt', 'T', None),)
		elif 0xf6 == iw:
			#  ['TEST', 'reg/mem8 imm8', 'F6', '/0 ib', '\n']
			# &c
			x = self.modRM(p, 8, self.asz)
			self.mne =("TEST", "TEST", "NOT", "NEG",
			    "MUL", "IMUL", "DIV", "IDIV")[x[2]]
			self.o.append("BYTE:")
			self.o.append(x[4])
			if x[2] < 2:
				self.o.append(self.imm(p, 8))
			else:
				raise X86Error(self.ia, "undefined")

		elif 0xf7 == iw:
			#  ['TEST', 'reg/mem16 imm16', 'F7', '/0 iw', '\n']
			#  ['TEST', 'reg/mem32 imm32', 'F7', '/0 id', '\n']
			#  ['TEST', 'reg/mem64 imm32', 'F7', '/0 id', '\n']
			# &c
			x = self.modRM(p, self.osz, self.asz)
			self.mne =("test", "test", "not", "neg",
			    "mul", "imul", "div", "idiv")[x[2]]
			self.o.append(x[4])
			if x[2] < 2:
				self.o.append(self.imm(p, self.osz))

		elif 0xfe == iw:
			x = self.modRM(p, 8, self.asz)
			if x[2] >= 2:
				self.unknown(p, adr, self.ia)
				return
			self.mne =("INC", "DEC")[x[2]]
			self.o.append(x[4])

		elif 0xff == iw:
			self.modRM(p, self.osz, self.asz)
			if self.mrm[2] == 0:
				self.__short(p, "inc", "Ev")
			elif self.mrm[2] == 2:
				self.mne = "CALL"
				self.o.append(x[4])
				# XXX: can we do better ?
				self.flow = (("call", "T", None),)
			elif self.mrm[2] == 6:
				self.__short(p, "push", "Ev")
	
		elif 0x0f01 == iw:
			x = self.modRM(p, 16, self.asz)
			if x[2] == 2:
				self.mne ="LGDT"
				self.o.append(x[4])
			else:
				self.unknown(p, adr, self.ia)
				return
		elif 0x0f20 == iw:
			#  ['MOV', 'reg32 CR', '0F 20', '/r', '\n']
			#  ['MOV', 'reg64 CR', '0F 20', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, 32, self.asz)
			self.o.append(x[4])
			self.o.append(cReg[x[2]])
		elif 0x0f22 == iw:
			#  ['MOV', 'CR reg32', '0F 22', '/r', '\n']
			#  ['MOV', 'CR reg64', '0F 22', '/r', '\n']
			self.mne = "MOV"
			x = self.modRM(p, 32, self.asz)
			self.o.append(cReg[x[2]])
			self.o.append(x[4])
		elif 0x0fb6 == iw:
			#  ['MOVZX', 'reg16 reg/mem8', '0F B6', '/r', '\n']
			#  ['MOVZX', 'reg32 reg/mem8', '0F B6', '/r', '\n']
			#  ['MOVZX', 'reg64 reg/mem8', '0F B6', '/r', '\n']
			self.mne = "MOVZX"
			x = self.modRM(p, 8, self.asz)
			self.o.append(gReg[self.osz][x[2]])
			self.o.append(x[4])
		elif 0x0fb7 == iw:
			#  ['MOVZX', 'reg32 reg/mem16', '0F B7', '/r', '\n']
			#  ['MOVZX', 'reg64 reg/mem16', '0F B7', '/r', '\n']
			self.mne = "movzwl"
			x = self.modRM(p, 16, self.asz)
			self.o.append(gReg[self.osz][x[2]])
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
		elif 0xdbe3 == iw:
			self.mne = "FNINIT"
		else:
			self.unknown(p, self.ia)
			return None

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
