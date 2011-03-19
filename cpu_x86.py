#!/usr/local/bin/python
#
# Intel x86 family CPU disassembler
#

from __future__ import print_function

ins={ }

idesc={}

try:
	f = open("x86_ins.txt")
except:
	f = open("../x86_ins.txt")

for i in f.readlines():
	if i[0] == "#":
		continue
	j = i.split("|")
	k = j[2].split()

	m = int(k[0],16)
	if m == 0x0f or m == 0xdb:
		m <<= 8
		m |= int(k[1],16)
	if not m in idesc:
		idesc[m] = list()
	idesc[m].append(j)

	if j[1] == "" and j[3] == "":
		ins[m] = j

f.close()

# Vol3 p364
reg8 = ("%al", "%cl", "%dl", "%bl", "%ah", "%ch", "%dh", "%bh")
reg16 = ("%ax", "%cx", "%dx", "%bx", "%sp", "%bp", "%si", "%di")
reg32 = ("%eax", "%ecx", "%edx", "%ebx", "%esp", "%ebp", "%esi", "%edi")
sReg = ("%es", "%cs", "%ss", "%ds", "%fs", "%gs", None, None)
cReg = ("%cr0", "%cr1", "%cr2", "%cr3", "%cr4", "%cr5", "%cr6", "%cr7")

gReg = {
	8:  reg8,
	16: reg16,
	32: reg32,
}

cc=("O", "NO", "B", "NB", "Z", "NZ", "BE", "NBE", 
    "S", "NS", "P", "NP", "L", "NL", "LE", "NLE")

shifts=("ROL", "ROR", "RCL", "RCR", "SHL", "SHR", "SAL", "SAR")
alu=("ADD", "OR", "ADC", "SBB", "AND", "SUB", "XOR", "CMP")

modrm16 = ("%bx+%si", "%bx+%di", "%bp+%si", "%bp+%di",
	   "%si", "%di", "%bp", "%bx")

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
		for i in range(0,32):
			j.append(p.m.rd(adr + i))

		f = open("/tmp/_x86.bin", "wb")
		f.write(j)
		f.close()
		print("--------------------------------------------------")
		call("objdump -b binary -D -mi386 -M" + self.arch +
		    " /tmp/_x86.bin", shell=True)
		print("--------------------------------------------------")

		m = p.m.rd(adr2)
		if m == 0x0f or m == 0xdb:
			m <<= 8
			m += p.m.rd(adr2 + 1)
		print("Adr: 0x%x Ins: 0x%x" % (adr, m))
		if m in idesc:
			for i in idesc[m]:
				print("# ", i)
		print("--------------------------------------------------")

	# Return:
	#	x[0] = len
	#	x[1] = mod
	#	x[2] = reg
	#	x[3] = rm
	#	x[4] = oper
	#
	def modRM(self, p, adr, osz, asz):
		modrm = p.m.rd(adr)
		l = 1
		mod = modrm >> 6
		reg = (modrm >> 3) & 7
		rm = modrm & 7
		ea = self.seg

		if mod == 3:
			ea = gReg[osz][rm]
			return (l, mod, reg, rm, ea)

		if asz == 16:
			if mod == 0 and rm == 6:
				x = p.m.s16(adr + l)
				l += 2
				ea += "(0x%04x)" % x
				return (l, mod, reg, rm, ea)
			else:
				rx = modrm16[rm]
		elif asz == 32:
			if rm == 4:
				sip = p.m.rd(adr + l)
				l += 1
				sip_s = 1 << (sip >> 6)
				sip_i = (sip >> 3) & 7
				sip_b = sip & 7
				print("SIP = %02x (%d %d %d)" % (sip, sip_s, sip_i, sip_b))
				print("Unhandled 32bit ModRM (SIP) @%x: %x = (%x %x %x)" % 
				    (adr, p.m.rd(adr), mod, reg, rm))
				if sip_i != 4:
					rx = reg32[sip_i] + "+"
					if sip_s > 1:
						rx += "*%d+" % sip_s
				else:
					rx = ""
				if sip_b != 5:
					rx += reg32[sip_b]
				else:
					print("Unhandled 32bit ModRM (rIP) @%x: %x = (%x %x %x)" % 
					    (adr, p.m.rd(adr), mod, reg, rm))
					return None
				print("RX= <%s>" % rx)
			elif mod == 0 and rm == 5:
				print("Unhandled 32bit ModRM (rIP) @%x: %x = (%x %x %x)" % 
				    (adr, p.m.rd(adr), mod, reg, rm))
				return None
			else:
				rx = reg32[rm]
		else:
			print("Unhandled ModRM %d-bit @%x: %x = (%x %x %x)" % 
			    (asz, adr, p.m.rd(adr), mod, reg, rm))
			assert False

		if mod == 0:
			ea = self.seg + "(" + rx + ")"
			return (l, mod, reg, rm, ea)

		if mod == 1:
			x = p.m.s8(adr + l)
			l += 1
			f = "0x%02x"
		elif mod == 2 and asz == 16:
			x = p.m.s16(adr + l)
			l += 2
			f = "0x%04x"
		elif mod == 2 and asz == 32:
			x = p.m.s32(adr + l)
			l += 4
			f = "0x%08x"
		else:
			print("Unhandled 32bit ModRM @%x: %x = (%x %x %x)" % 
			    (adr, p.m.rd(adr), mod, reg, rm))
			assert False

		if x < 0:
			ea += "(" + rx + "-" + f % (-x) + ")" 
		else:
			ea += "(" + rx + "+" + f % x + ")" 
		return (l, mod, reg, rm, ea)

	# Return:
	#	x[0] = len
	#	x[1] = oper
	def dir(self, p, adr, sz):
		if sz == 8:
			w =  p.m.rd(adr)
			return (1, "0x%02x" % w, w)
		if sz == 16:
			w =  p.m.w16(adr)
			return (2, "0x%04x" % w, w)
		if sz == 32:
			w =  p.m.w32(adr)
			return (4, "0x%08x" % w, w)
		assert False

	# Return:
	#	x[0] = len
	#	x[1] = oper
	def imm(self, p, adr, sz):
		if sz == 8:
			return (1, "#0x%02x" % p.m.rd(adr))
		if sz == 16:
			return (2, "#0x%04x" % p.m.w16(adr))
		if sz == 32:
			return (4, "#0x%08x" % p.m.w32(adr))
		assert False

	def disass(self, p, adr, priv = None):
		try:
			iw = p.m.rd(adr)
			iw2 = p.m.rd(adr + 1)
		except:
			print("FETCH failed:", adr)
			return

		if iw == 0xff and iw2 == 0xff:
			return
		if iw == 0x00 and iw2 == 0x00:
			return

		self.osz = self.mosz
		self.asz = self.masz
		self.ia = adr
		
		l = 1
		o=list()
		da=None
		mne=None
		flow=None
		self.seg = ""

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
			iw = p.m.rd(adr + l)
			l += 1

		# Two-byte instructions
		if iw == 0x0f or iw == 0xdb:
			iw <<= 8
			iw |= p.m.rd(adr + l)
			l += 1

		if 0x00 == iw & 0xffcf:
			#  ['ADD', 'reg/mem8 reg8', '00', '/r', '\n']
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(reg8[x[2]])
			o.append(x[4])
		elif 0x01 == iw & 0xffcf:
			#  ['ADD', 'reg/mem16 reg16', '01', '/r', '\n']
			#  ['ADD', 'reg/mem32 reg32', '01', '/r', '\n']
			#  ['ADD', 'reg/mem64 reg64', '01', '/r', '\n']
			# &c
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(gReg[self.osz][x[2]])
		elif 0x02 == iw & 0xffcf:
			#  ['XOR', 'reg8 reg/mem8', '32', '/r the', '\n']
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(reg8[x[2]])
		elif 0x03 == iw & 0xffcf:
			#  ['ADD', 'reg16 reg/mem16', '03', '/r', '\n']
			#  etc
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x04 == iw & 0xffcf:
			#  ['ADD', 'reg16 reg/mem16', '03', '/r', '\n']
			#  etc
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			o.append("%al")
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0x05 == iw & 0xffcf:
			#  ['ADD', 'AX imm16', '25', 'iw', '\n']
			#  ['ADD', 'EAX imm32', '25', 'id', '\n']
			#  ['ADD', 'RAX imm32', '25', 'id', '\n']
			#  &c
			mne=("ADD", "ADC", "AND", "XOR")[(iw>>4) & 3]
			o.append(gReg[self.osz][0])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0x06 == iw:
			#  ['PUSH', 'ES', '06', '', '\n']
			mne="PUSH"
			o.append("%es")
		elif 0x07 == iw:
			#  ['POP', 'ES', '07', '', '\n']
			mne="POP"
			o.append("%es")
		elif 0x08 == iw & 0xffcf:
			#  ['CMP', 'reg/mem8 reg8', '38', '/r', '\n']
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(reg8[x[2]])
			o.append(x[4])
		elif 0x09 == iw & 0xffcf:
			#  ['CMP', 'reg/mem16 reg16', '39', '/r', '\n']
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(gReg[self.osz][x[2]])
		elif 0x0a == iw & 0xffcf:
			#  ['OR', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['SBB', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['SUB', 'reg8 reg/mem8', '2A', '/r', '\n']
			#  ['CMP', 'reg8 reg/mem8', '2A', '/r', '\n']
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(reg8[x[2]])
			o.append(x[4])
		elif 0x0b == iw & 0xffcf:
			#  ['OR', 'reg16 reg/mem16', '2B', '/r', '\n']
			#  ['OR', 'reg32 reg/mem32', '2B', '/r', '\n']
			#  ['OR', 'reg64 reg/mem64', '2B', '/r', '\n']
			#  &c
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			mne = "SUB"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x0c == iw & 0xffcf:
			#  ['OR', 'AL imm8', '0C', 'ib', '\n']
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			o.append("%al")
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0x0d == iw & 0xffcf:
			#  ['OR', 'AX imm16', '0D', 'iw', '\n']
			#  ['OR', 'EAX imm32', '0D', 'id', '\n']
			#  ['OR', 'RAX imm32', '0D', 'id', '\n']
			#  &c
			mne=("OR", "SBB", "SUB", "CMP")[(iw>>4) & 3]
			o.append(gReg[self.osz][0])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0x0e == iw:
			mne="PUSH"
			o.append("%cs")
		elif 0x16 == iw:
			mne="PUSH"
			o.append("%ss")
		elif 0x1E == iw:
			mne="PUSH"
			o.append("%ds")
		elif 0x1F == iw:
			mne="POP"
			o.append("%ds")
		elif 0x40 == iw & 0xfff8:
			mne="INC"
			o.append(gReg[self.osz][iw & 0x07])
		elif 0x48 == iw & 0xfff8:
			mne="DEC"
			o.append(gReg[self.osz][iw & 0x07])
		elif 0x50 == iw & 0xfff8:
			mne="PUSH"
			o.append(gReg[self.osz][iw & 0x07])
		elif 0x58 == iw & 0xfff8:
			mne="POP"
			o.append(gReg[self.osz][iw & 0x07])
		elif 0x68 == iw:
			#  ['PUSH', 'imm16', '68', 'iw', '\n']
			mne="PUSH"
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0x6a == iw:
			#  ['PUSH', 'imm8', '6A', 'ib', '\n']
			mne="PUSH"
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0x70 == iw & 0xfff0:
			#  ['Jcc', 'rel8off', '75', 'cb', '\n']
			cx = cc[iw & 0xf]
			mne = "J" + cx
			da = adr + 2 + p.m.s8(adr + 1)
			l += 1
			o.append("0x%x" % da)
			flow = (
			    ('cond', cx, da),
			    ('cond', cc[(iw ^ 1) & 0xf], adr + 2)
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
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			mne = alu[x[2]]
			o.append(x[4])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])

		elif 0x81 == iw:
			#  ['ADC', 'reg/mem16 imm16', '81', '/2 iw', '\n']
			#  ['ADC', 'reg/mem32 imm32', '81', '/2 id', '\n']
			#  ['ADC', 'reg/mem64 imm32', '81', '/2 id', '\n']
			#  &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne = alu[x[2]]
			o.append(x[4])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0x83 == iw:
			#  ['ADC', 'reg/mem16 imm8', '83', '/2 ib', '\n']
			#  ['ADC', 'reg/mem32 imm8', '83', '/2 ib', '\n']
			#  ['ADC', 'reg/mem64 imm8', '83', '/2 ib', '\n']
			#  &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne = alu[x[2]]
			o.append(x[4])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0x85 == iw:
			#  ['TEST', 'reg/mem16 reg16', '86', '/r', '\n']
			mne = "TEST"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x86 == iw:
			#  ['XCHG', 'reg/mem8 reg8', '86', '/r', '\n']
			mne = "XCHG"
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(reg8[x[2]])
			o.append(x[4])
		elif 0x87 == iw:
			#  ['XCHG', 'reg/mem16 reg16', '87', '/r', '\n']
			mne = "XCHG"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x88 == iw:
			#  ['MOV', 'reg/mem8 reg8', '88', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(reg8[x[2]])
		elif 0x89 == iw:
			#  ['MOV', 'reg/mem16 reg16', '89', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(gReg[self.osz][x[2]])
		elif 0x8a == iw:
			# ['MOV', 'reg8 reg/mem8', '8A', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(reg8[x[2]])
			o.append(x[4])
		elif 0x8b == iw:
			# ['MOV', 'reg16 reg/mem16', '8A', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x8c == iw:
			#  ['MOV', 'reg16/32/64/mem16 segReg', '8C', '/r', '\n']
			mne= "MOV"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(sReg[x[2]])
		elif 0x8d == iw:
			#  ['LEA', 'reg16 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg32 mem', '8D', '/r', '\n']
			#  ['LEA', 'reg64 mem', '8D', '/r', '\n']
			mne= "LEA"
			# XXX: osz or asz ?? 
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x8e == iw:
			#  ['MOV', 'segReg reg/mem16', '8E', '/r', '\n']
			mne= "MOV"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			o.append(sReg[x[2]])
			o.append(x[4])
		elif 0x8f == iw:
			x = self.modRM(p, adr + l, self.osz, self.asz)
			if x[2] == 0:
				l += x[0]
				mne = "POP"
				o.append(x[4])
			else:
				self.unknown(p, adr, self.ia)
				return
		elif 0x90 == iw & 0xfff8:
			mne= "XCHG"
			assert(self.osz == 16)
			o.append("%ax")
			o.append(gReg[self.osz][iw & 7])
		elif 0x9b == iw:
			mne = "FWAIT"
		elif 0xa0 == iw:
			#  ['MOV', 'AL moffset8', 'A0', '', '\n']
			mne="MOV"
			x = self.dir(p, adr + l, self.asz)
			l += x[0]
			o.append("%al")
			o.append(x[1])
		elif 0xa1 == iw:
			#  ['MOV', 'AX moffset16', 'A1', '', '\n']
			#  ['MOV', 'AX moffset32', 'A1', '', '\n']
			#  ['MOV', 'AX moffset64', 'A1', '', '\n']
			mne="MOV"
			x = self.dir(p, adr + l, self.asz)
			l += x[0]
			o.append(x[1])
			o.append(gReg[self.osz][0])
		elif 0xa2 == iw:
			#  ['MOV', 'AL moffset8', 'A0', '', '\n']
			mne="MOV"
			x = self.dir(p, adr + l, self.asz)
			l += x[0]
			o.append(x[1])
			o.append("%al")
		elif 0xa3 == iw:
			#  ['MOV', 'moffset16 AX', 'A3', '', '\n']
			mne="MOV"
			o.append(gReg[self.osz][0])
			x = self.dir(p, adr + l, self.asz)
			l += x[0]
			o.append(x[1])
		elif 0xa8 == iw:
			#  ['ADD', 'reg/mem8 reg8', '00', '/r', '\n']
			mne="TEST"
			o.append("%al")
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0xa9 == iw:
			#  ['TEST', 'AX imm16', 'A9', 'iw', '\n']
			#  ['TEST', 'EAX imm32', 'A9', 'id', '\n']
			#  ['TEST', 'RAX imm32', 'A9', 'id', '\n']
			mne="TEST"
			o.append(gReg[self.osz][0])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0xb0 == iw & 0xfff8:
			#  ['MOV', 'reg8 imm8', 'B0', '+rb ib', '\n']
			mne="MOV"
			o.append(reg8[iw & 7])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0xb8 == iw & 0xfff8:
			#  ['MOV', 'reg16 imm16', 'B0', '+rw iw', '\n']
			#  ['MOV', 'reg32 imm32', 'B0', '+rd id', '\n']
			#  ['MOV', 'reg64 imm64', 'B0', '+rq iq', '\n']
			mne="MOV"
			o.append(gReg[self.osz][iw & 7])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0xc0 == iw:
			#  ['RCL', 'reg/mem8 imm8', 'C0', '/2 ib', '\n']
			#  &c
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0xc1 == iw:
			#  ['RCL', 'reg/mem8 imm8', 'C0', '/2 ib', '\n']
			#  &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0xc3 == iw:
			#  ['RET', '', 'E3', '', '\n']
			mne="RET"
			flow = (('ret', 'T', None),)
		elif 0xc6 == iw:
			#  ['MOV', 'reg/mem8 imm8', 'C6', '/0 ib', '\n']
			# XXX: disagreement with objdump
			mne="MOV"
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			if x[2] != 0:
				return
			o.append(x[4])
			y = self.imm(p, adr + l, 8)
			l += y[0]
			o.append(y[1])
		elif 0xc7 == iw:
			#  ['MOV', 'reg/mem16 imm16', 'C7', '/0 iw', '\n']
			mne="MOV"
			x = self.modRM(p, adr + l, self.osz, self.asz)
			if x == None:
				return
			l += x[0]
			if x[2] != 0:
				return
			o.append(x[4])
			x = self.imm(p, adr + l, self.osz)
			l += x[0]
			o.append(x[1])
		elif 0xc8 == iw:
			#  ['ENTER', 'imm16 0', 'C8', 'iw 00', '\n']
			#  ['ENTER', 'imm16 1', 'C8', 'iw 01', '\n']
			#  ['ENTER', 'imm16 imm8', 'C8', '', '\n']
			mne="ENTER"
			x = self.imm(p, adr + l, 16)
			l += x[0]
			o.append(x[1])
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
		elif 0xcd == iw:
			#  ['INT', 'imm8', 'CD', 'ib', '\n']
			mne="INT"
			x = self.imm(p, adr + l, 8)
			l += x[0]
			o.append(x[1])
			flow = (('call', 'T', None),)
		elif 0xcf == iw:
			mne="IRET"
			flow = (('ret', 'T', None),)
		elif 0xd0 == iw:
			#  ['ROL', 'reg/mem8 1', 'D0', '/0', '\n']
			#  &c
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
		elif 0xd1 == iw:
			#  ['RCL', 'reg/mem16 1', 'D1', '/2', '\n']
			#  &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
		elif 0xd2 == iw:
			#  ['RCL', 'reg/mem8 CL', 'D2', '/2 bit', '\n']
			#  &c
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
			o.append("%cl")
		elif 0xd3 == iw:
			#  ['RCL', 'reg/mem16 CL', 'D3', '/2 bit', '\n']
			#  &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne = shifts[x[2]]
			o.append(x[4])
			o.append("%cl")
		elif 0xd9 == iw:
			# FP
			x = self.modRM(p, adr + l, self.osz, self.asz)
			if x[1] != 3 and x[3] == 6:
				l += 1
				mne="FNSTCW"
				x = self.imm(p, adr + l, 16)
				l += x[0]
				o.append(x[1])
			else:
					
				print(x)
				self.unknown(p, adr, self.ia)
				return
		elif 0xe0 == iw & 0xfffc:
			#  ['LOOP', 'rel8off', 'E2', 'cb', '\n']
			mne = ("LOOPNE", "LOOPE", "LOOP", "JCXZ")[iw & 3]
			da = adr + 2 + p.m.s8(adr + 1)
			l += 1
			o.append("0x%x" % da)
			flow = (
			    ('cond', "XXX1", da),
			    ('cond', "XXX2",  adr + l)
			)
		elif 0xe4 == iw:
			#  ['IN', 'AL imm8 ', 'E4', 'ib', '\n']
			mne="OUT"
			o.append("%al")
			o.append("#0x%02x" % p.m.rd(adr+l))
			l += 1
		elif 0xe6 == iw:
			#  ['OUT', 'imm8 AL', 'E6', 'ib', '\n']
			mne="OUT"
			o.append("#0x%02x" % p.m.rd(adr+l))
			l += 1
			o.append("%al")
		elif 0xe7 == iw:
			#  ['OUT', 'imm8 AX', 'E7', 'ib', '\n']
			#  ['OUT', 'imm8 EAX', 'E7', 'ib', '\n']
			mne="OUT"
			o.append("#0x%02x" % p.m.rd(adr+l))
			l += 1
			o.append(gReg[self.osz][0])
		elif 0xe8 == iw:
			if self.asz == 16:
				oo = p.m.s16(adr + l)
				l += 2
			elif self.asz == 32:
				oo = p.m.s32(adr + l)
				l += 4
			else:
				assert False
			da = adr + l + oo
			mne="CALL"
			o.append("0x%x" % da)
			flow=(("call", "T", da),)
		elif 0xe9 == iw:
			#  ['JMP', 'rel16off', 'E9', 'cw', '\n']
			#  ['JMP', 'rel32off', 'E9', 'cd', '\n']
			mne="JMP"
			if self.osz == 16:
				da = adr + 3 + p.m.s16(adr + l)
				l += 2
			else:
				da = adr + 5 + p.m.s32(adr + l)
				l += 4
			o.append("#0x%x" % da)
			flow=(('cond', 'T', da),)
		elif 0xea == iw:
			#  ['JMP', 'FAR pntr16:16', 'EA', 'cd', '\n']
			#  ['JMP', 'FAR pntr16:32', 'EA', 'cp', '\n']
			mne="JMP"
			if self.asz == 16:
				off = p.m.w16(adr + l)
				fx = "0x%04x"
				l += 2
			else:
				off = p.m.w32(adr + l)
				fx = "0x%08x"
				l += 4
			sg = p.m.w16(adr + l)
			l += 2
			o.append("FAR")
			o.append("0x%04x" % sg)
			o.append(fx % off)
			if self.mode == "real":
				flow=(('cond', 'T', (sg << 4) + off),)
			else:
				assert False
		elif 0xeb == iw:
			#  ['JMP', 'rel8off', 'EB', 'cb', '\n']
			mne = "JMP"
			da = adr + 2 + p.m.s8(adr + l)
			l += 1
			o.append("0x%x" % da)
			flow=(('cond', 'T', da),)
		elif 0xec == iw:
			#  ['IN', 'AL DX', 'EC', '', '\n']
			mne="IN"
			o.append("%al")
			o.append("(%dx)")
		elif 0xed == iw:
			#  ['IN', 'AX DX', 'ED', '', '\n']
			#  ['IN', 'EAX DX', 'ED', '', '\n']
			mne="IN"
			o.append(gReg[self.osz][0])
			o.append("(%dx)")
		elif 0xee == iw:
			#  ['OUT', 'DX AL ', 'EE', '', '\n']
			mne="OUT"
			o.append("(%dx)")
			o.append("%al")
		elif 0xef == iw:
			#  ['OUT', 'DX AX ', 'EF', '', '\n']
			#  ['OUT', 'DX EAX ', 'EF', '', '\n']
			mne="OUT"
			o.append("(%dx)")
			o.append(gReg[self.osz][0])
		elif 0xf4 == iw:
			#  ['HLT', '', 'E3', '', '\n']
			mne="HLT"
			flow = (('halt', 'T', None),)
		elif 0xf6 == iw:
			#  ['TEST', 'reg/mem8 imm8', 'F6', '/0 ib', '\n']
			# &c
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			mne=("TEST", "TEST", "NOT", "NEG",
			    "MUL", "IMUL", "DIV", "IDIV")[x[2]]
			o.append("BYTE:")
			o.append(x[4])
			if x[2] < 2:
				x = self.imm(p, adr + l, 8)
				l += x[0]
				o.append(x[1])

		elif 0xf7 == iw:
			#  ['TEST', 'reg/mem16 imm16', 'F7', '/0 iw', '\n']
			#  ['TEST', 'reg/mem32 imm32', 'F7', '/0 id', '\n']
			#  ['TEST', 'reg/mem64 imm32', 'F7', '/0 id', '\n']
			# &c
			x = self.modRM(p, adr + l, self.osz, self.asz)
			l += x[0]
			mne=("TEST", "TEST", "NOT", "NEG",
			    "MUL", "IMUL", "DIV", "IDIV")[x[2]]
			o.append(x[4])
			if x[2] < 2:
				x = self.imm(p, adr + l, self.osz)
				l += x[0]
				o.append(x[1])

		elif 0xfe == iw:
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			if x[2] >= 2:
				self.unknown(p, adr, self.ia)
				return
			mne=("INC", "DEC")[x[2]]
			o.append(x[4])

		elif 0xff == iw:
			# self.unknown(p, adr, self.ia)
			x = self.modRM(p, adr + l, self.osz, self.asz)
			if x[2] == 0:
				l += x[0]
				mne = "INC"
				o.append(x[4])
			elif x[2] == 2:
				l += x[0]
				mne = "CALL"
				o.append(x[4])
				# XXX: can we do better ?
				flow = (("call", "T", None),)
			elif x[2] == 6:
				l += x[0]
				mne = "PUSH"
				o.append(x[4])
			else:
				self.unknown(p, adr, self.ia)
				return

	
		elif 0x0f01 == iw:
			x = self.modRM(p, adr + l, 16, self.asz)
			l += x[0]
			if x[2] == 2:
				mne="LGDT"
				o.append(x[4])
			else:
				self.unknown(p, adr, self.ia)
				return
		elif 0x0f20 == iw:
			#  ['MOV', 'reg32 CR', '0F 20', '/r', '\n']
			#  ['MOV', 'reg64 CR', '0F 20', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, 32, self.asz)
			l += x[0]
			o.append(x[4])
			o.append(cReg[x[2]])
		elif 0x0f22 == iw:
			#  ['MOV', 'CR reg32', '0F 22', '/r', '\n']
			#  ['MOV', 'CR reg64', '0F 22', '/r', '\n']
			mne = "MOV"
			x = self.modRM(p, adr + l, 32, self.asz)
			l += x[0]
			o.append(cReg[x[2]])
			o.append(x[4])
		elif 0x0fb6 == iw:
			#  ['MOVZX', 'reg16 reg/mem8', '0F B6', '/r', '\n']
			#  ['MOVZX', 'reg32 reg/mem8', '0F B6', '/r', '\n']
			#  ['MOVZX', 'reg64 reg/mem8', '0F B6', '/r', '\n']
			mne = "MOVZX"
			x = self.modRM(p, adr + l, 8, self.asz)
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x0fb7 == iw:
			#  ['MOVZX', 'reg32 reg/mem16', '0F B7', '/r', '\n']
			#  ['MOVZX', 'reg64 reg/mem16', '0F B7', '/r', '\n']
			mne = "MOVZX"
			x = self.modRM(p, adr + l, 16, self.asz)
			if x == None:
				return
			l += x[0]
			o.append(gReg[self.osz][x[2]])
			o.append(x[4])
		elif 0x0f80 == iw & 0xfff0:
			#  ['JB', 'rel16off', '0F 82', 'cw', '\n']
			cx = cc[iw & 0xf]
			mne = "J" + cx
			if self.asz == 16:
				of = p.m.s16(adr + l)
				l += 2
			elif self.asz == 32:
				of = p.m.s32(adr + l)
				l += 4
			else:
				assert False
			da = adr + l + of
			o.append("0x%04x" % da)
			flow = (
			    ('cond', cx, da),
			    ('cond', cc[(iw ^ 1) & 0xf], adr + l)
			)
		elif 0xdbe3 == iw:
			mne = "FNINIT"
		elif iw in ins:
			ii = ins[iw]
			mne = ii[0]
		else:
			self.unknown(p, adr, self.ia)
			return

		x = p.t.add(adr, adr + l, "ins")
		x.a['mne'] = mne
		x.a['oper'] = o
		if flow != None:
			x.a['flow'] = flow
		x.render = self.render
		p.ins(x, self.disass)
