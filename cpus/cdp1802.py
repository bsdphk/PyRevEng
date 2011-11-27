#!/usr/local/bin/python3.2

doc = """
IDL     Idle                                    00      2
LDN r   Load D via N (for r = 1 to F)           0r      2
INC r   Increment Register                      1r      2
DEC r   Decrement Register                      2r      2
BR a    Branch unconditionally                  30 aa   2
BQ a    Branch if Q is on                       31 aa   2
BZ a    Branch on Zero                          32 aa   2
BDF a   Branch if DF is 1                       33 aa   2
B1 a    Branch on External Flag 1               34 aa   2
B2 a    Branch on External Flag 2               35 aa   2
B3 a    Branch on External Flag 3               36 aa   2
B4 a    Branch on External Flag 4               37 aa   2
SKP     Skip one byte                           38      2
BNQ a   Branch if Q is off                      39 aa   2
BNZ a   Branch on Not Zero                      3A aa   2
BNF a   Branch if DF is 0                       3B aa   2
BN1 a   Branch on Not External Flag 1           3C aa   2
BN2 a   Branch on Not External Flag 2           3D aa   2
BN3 a   Branch on Not External Flag 3           3E aa   2
BN4 a   Branch on Not External Flag 4           3F aa   2
LDA r   Load D and Advance                      4r      2
STR r   Store D into memory                     5r      2
IRX     Increment R(X)                          60      2
INP p   Input to memory and D (for p = 9 to F)  6p      2
OUT p   Output from memory (for p = 1 to 7)     6p      2
RET     Return                                  70      2
DIS     Return and Disable Interrupts           71      2
LDXA    Load D via R(X) and Advance             72      2
STXD    Store D via R(X) and Decrement          73      2
ADC     Add with Carry                          74      2
SDB     Subtract D from memory with Borrow      75      2
SHRC    Shift D Right with Carry                76      2
SMB     Subtract Memory from D with Borrow      77      2
SAV     Save T                                  78      2
MARK    Save X and P in T                       79      2
REQ     Reset Q                                 7A      2
SEQ     Set Q                                   7B      2
ADCI b  Add with Carry Immediate                7C bb   2
SDBI b  Subtract D with Borrow, Immediate       7D bb   2
SHLC    Shift D Left with Carry                 7E      2
SMBI b  Subtract Memory with Borrow, Immediate  7F bb   2
GLO r   Get Low byte of Register                8r      2
GHI r   Get High byte of Register               9r      2
PLO r   Put D in Low byte of register           Ar      2
PHI r   Put D in High byte of register          Br      2
LBR aa  Long Branch unconditionally             C0 aaaa 3
LBQ aa  Long Branch if Q is on                  C1 aaaa 3
LBZ aa  Long Branch if Zero                     C2 aaaa 3
LBDF aa Long Branch if DF is 1                  C3 aaaa 3
NOP     No Operation                            C4      3
LSNQ    Long Skip if Q is off                   C5      3
LSNZ    Long Skip if Not Zero                   C6      3
LSNF    Long Skip if DF is 0                    C7      3
LSKP    Long Skip                               C8      3
LBNQ aa Long Branch if Q is off                 C9 aaaa 3
LBNZ aa Long Branch if Not Zero                 CA aaaa 3
LBNF aa Long Branch if DF is 0                  CB aaaa 3
LSIE    Long Skip if Interrupts Enabled         CC      3
LSQ     Long Skip if Q is on                    CD      3
LSZ     Long Skip if Zero                       CE      3
LSDF    Long Skip if DF is 1                    CF      3
SEP r   Set P                                   Dr      2
SEX r   Set X                                   Er      2
LDX     Load D via R(X)                         F0      2
OR      Logical OR                              F1      2
AND     Logical AND                             F2      2
XOR     Exclusive OR                            F3      2
ADD     Add                                     F4      2
SD      Subtract D from memory                  F5      2
SHR     Shift D Right                           F6      2
SM      Subtract Memory from D                  F7      2
LDI b   Load D Immediate                        F8 bb   2
ORI b   OR Immediate                            F9 bb   2
ANI b   AND Immediate                           FA bb   2
XRI b   Exclusive OR, Immediate                 FB bb   2
ADI b   Add Immediate                           FC bb   2
SDI b   Subtract D from memory Immediate byte   FD bb   2
SHL     Shift D Left                            FE      2
SMI b   Subtract Memory from D, Immediate       FF bb   2
"""

unknown_state = {
	"/DF":		( 1, None),
	"/Q":		( 1, None),
	"/P":		( 4, None),
	"/D":		( 8, None),
	"/X":		( 4, None),
	"/IE":		( 1, None),
	"/R0.0":	(8, None),
	"/R1.0":	(8, None),
	"/R2.0":	(8, None),
	"/R3.0":	(8, None),
	"/R4.0":	(8, None),
	"/R5.0":	(8, None),
	"/R6.0":	(8, None),
	"/R7.0":	(8, None),
	"/R8.0":	(8, None),
	"/R9.0":	(8, None),
	"/R10.0":	(8, None),
	"/R11.0":	(8, None),
	"/R12.0":	(8, None),
	"/R13.0":	(8, None),
	"/R14.0":	(8, None),
	"/R15.0":	(8, None),
	"/R0.1":	(8, None),
	"/R1.1":	(8, None),
	"/R2.1":	(8, None),
	"/R3.1":	(8, None),
	"/R4.1":	(8, None),
	"/R5.1":	(8, None),
	"/R6.1":	(8, None),
	"/R7.1":	(8, None),
	"/R8.1":	(8, None),
	"/R9.1":	(8, None),
	"/R10.1":	(8, None),
	"/R11.1":	(8, None),
	"/R12.1":	(8, None),
	"/R13.1":	(8, None),
	"/R14.1":	(8, None),
	"/R15.1":	(8, None),
}

reset_state = {
	"/Q":		( 1, 0),
	"/P":		( 4, 0),
	"/X":		( 4, 0),
	"/IE":		( 1, 1),
	"/R0.0":	(8, 0),
	"/R0.1":	(8, 0),
}

import model
import copy
import disass

class model_cdp1802(disass.assy):
	def __init__(self):
		model.model.__init__(self);
		self.verbs["MEM"] = (self.verb_mem, "adr")
		self.verbs["BUS"] = (self.verb_bus, "val", "adr")

	def render_state(self, state):
		if state == None:
			return "<no_state>"
		s = ""
		for i in unknown_state:
			if i[1] == "R":
				continue
			if state[i][1] != None:
				if state[i][0] == 8:
					s += i + "=0x%02x " % state[i][1]
				else:
					s += i + "=0x%x " % state[i][1]
		for i in range(0,16):
			r = "/R%d" % i
			r0 = state[r + ".0"]
			r1 = state[r + ".1"]
			if r0[1] == None and r1[1] == None:
				continue
			s += r + "="
			if r1[1] == None:
				s += "??"
			else:
				s += "%02x" % r1[1]
			if r0[1] == None:
				s += "??"
			else:
				s += "%02x" % r0[1]
			s += " "
		return s

	def setreg(self, p, state, reg, val):
		#print("SETREG", reg, val)
		assert(type(reg) == str)
		if reg == "/R(P)":
			rx = state["/P"]
			if rx[1] == None:
				# XXX: clear all regs ?
				return
			return self.setreg(p, state, "/R%d" % rx[1], val)
		elif reg == "/R(X)":
			rx = state["/X"]
			if rx[1] == None:
				return (16, None)
			return self.setreg(p, state, "/R%d" % rx[1], val)
		elif reg + ".0" in state:
			assert(val[0] == 16)
			if val[1] == None:
				state[reg + ".0"] = (8, None)
				state[reg + ".1"] = (8, None)
			else:
				state[reg + ".0"] = (8, val[1] & 0xff)
				state[reg + ".1"] = (8, val[1] >> 8)
		else:
			model.model.setreg(self, p, state, reg, val)
		

	def getreg(self, p, state, reg):
		assert(type(reg) == str)
		if reg == "/R(P)":
			rx = state["/P"]
			if rx[1] == None:
				return (16, None)
			return self.getreg(p, state, "/R%d" % rx[1])
		elif reg == "/R(X)":
			rx = state["/X"]
			if rx[1] == None:
				return (16, None)
			return self.getreg(p, state, "/R%d" % rx[1])
		elif reg + ".0" in state:
			r0 = state[reg + ".0"]
			r1 = state[reg + ".1"]
			if r0[1] == None or r1[1] == None:
				return (16, None)
			return (16, r1[1] << 8 | r0[1])
		else:
			return model.model.getreg(self, p, state, reg)

	def verb_mem(self, p, state, expr):
		#print("MEM", expr)
		v = self.eval(p, state, expr[1])
		if len(expr) == 3:
			return None
		if v[1] == None:
			return (8, None)
		return (8, p.m.rd(v[1]))

	def verb_bus(self, p, state, expr):
		return None
		


class cdp1802(disass.assy):
	def __init__(self, p, name = "cdp1802"):
		disass.assy.__init__(self, p, name)
		#self.model = model_cdp1802()

	def vectors(self, p):
		ss = copy.deepcopy(unknown_state)
		for i in reset_state:
			ss[i] = reset_state[i]
		x = self.disass(0)

	def do_disass(self, adr, ins):
		assert ins.lo == adr
		assert ins.status == "prospective"

		p = self.p

		iw = p.m.rd(adr)
		nw = p.m.rd(adr + 1)

		#print("cdp1802.disass(0x%x, " % adr, "%02x" % iw, ")")
		ireg = iw & 0xf0
		nreg = iw & 0x0f

		model = None
		model = ("SEQ", ("INC", "/R(P)"))
		mne = None
		arg = None
		length = 1
		#state = priv
		state = None

		if iw == 0xd4:	
			# XXX: hack
			da = p.m.b16(adr + 1)
			mne = "xcall"
			arg = "0x%04x" % da
			length = 3
			ins.flow = ("call", "T", da)
			model = None
		elif iw == 0xd5:	
			# XXX: hack
			mne = "xret"
			ins.flow = ("ret", "T", None)
			model = None

		#-----------------------------------------------
		# NB: Same order as data sheet

		#-----------------------------------------------
		# MEMORY REFERENCE

		elif ireg == 0x00 and nreg > 0:
			# LDN r   Load D via N (for r = 1 to F)
			mne = "ldn"
			arg = "%d" % nreg
			model += ( ("=", "/D", ("MEM", "/R%d" % nreg)), )
		elif ireg == 0x40:
			# LDA r   Load D and Advance
			mne = "lda"
			arg = "%d" % nreg
			model += (
			    ("=", "/D", ("MEM", "/R%d" % nreg)),
			    ("INC", "/R%d" % nreg),
			)
		elif iw == 0xf0:
			# LDX     Load D via R(X)
			mne = "ldx"
			model += ( ("=", "/D", ("MEM", "/R(X)")), )
		elif iw == 0x72:
			# LDXA    Load D via R(X) and Advance
			mne = "ldxa"
			model += (
			    ("=", "/D", ("MEM", "/R(X)")),
			    ("INC", "/R(X)"),
			)
		elif iw == 0xf8:
			# LDI b   Load D Immediate
			mne = "ldi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D", "#0x%02x" % nw),
			    ("INC", "/R(P)"),
			)
		elif ireg == 0x50:
			# STR r   Store D into memory
			mne = "str"
			arg = "%d" % nreg
			model += ( ("MEM", "/R%d" % nreg, "/D"), )
		elif iw == 0x73:
			# STXD    Store D via R(X) and Decrement
			mne = "stxd"
			model += (
			    ("MEM", "/R(X)", "/D"),
			    ("DEC", "/R(X)"),
			)

		#-----------------------------------------------
		# REGISTER OPERATIONS

		elif ireg == 0x10:
			# INC r   Increment Register
			mne = "inc"
			arg = "%d" % nreg
			model += ( ("INC", "/R%d" % nreg), )
		elif ireg == 0x20:
			# DEC r   Decrement Register
			mne = "dec"
			arg = "%d" % nreg
			model += ( ("DEC", "/R%d" % nreg), )
		elif iw == 0x60:
			# IRX     Increment R(X)
			mne = "irx"
			model += ( ("INC", "/X"), )
		elif ireg == 0x80:
			# GLO r   Get Low byte of Register
			mne = "glo"
			arg = "%d" % nreg
			model += ( ("=", "/D", "/R%d.0" % nreg), )
		elif ireg == 0xa0:
			# PLO r   Put D in Low byte of register
			mne = "plo"
			arg = "%d" % nreg
			model += ( ("=", "/R%d.0" % nreg, "/D"), )
		elif ireg == 0x90:
			# GHI r   Get High byte of Register
			mne = "ghi"
			arg = "%d" % nreg
			model += ( ("=", "/D", "/R%d.1" % nreg), )
		elif ireg == 0xb0:
			# PHI r   Put D in High byte of register
			mne = "phi"
			arg = "%d" % nreg
			model += ( ("=", "/R%d.1" % nreg, "/D"), )

		#-----------------------------------------------
		# LOGIC OPERATIONS

		elif iw == 0xf1:
			# OR      Logical OR
			mne = "or"
			model += (
			    ("=", "/D", ("OR", "/D", ("MEM", "/R(X)"))),
			)
		elif iw == 0xf9:
			# ORI b   OR Immediate
			mne = "ori"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D", ("OR", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
		elif iw == 0xf3:
			# XOR     Exclusive OR
			mne = "xor"
			model += (
			    ("=", "/D", ("XOR", "/D", ("MEM", "/R(X)"))),
			)
		elif iw == 0xfb:
			# XRI b   Exclusive OR, Immediate
			mne = "xri"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D", ("XOR", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
		elif iw == 0xf2:
			# AND     Logical AND
			mne = "and"
			model += (
			    ("=", "/D", ("AND", "/D", ("MEM", "/R(X)"))),
			)
		elif iw == 0xfa:
			# ANI b   AND Immediate
			mne = "ani"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D", ("AND", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
		elif iw == 0xf6:
			# SHR     Shift D Right
			mne = "shr"
			model += (
			    ("=", "/D", (">>", "/D", "#0x0", "#0b0", "/DF")),
			)
		elif iw == 0x76:
			# SHRC    Shift D Right with Carry
			mne = "shrc"
			model += (
			    ("=", "/D", (">>", "/D", "#0x0", "/DF", "/DF")),
			)
		elif iw == 0xfe:
			# SHL     Shift D Left
			mne = "shl"
			model += (
			    ("=", "/D", ("<<", "/D", "#0x0", "#0b0", "/DF")),
			)
		elif iw == 0x7e:
			# SHLC    Shift D Left with Carry
			mne = "shlc"
			model += (
			    ("=", "/D", ("<<", "/D", "#0x0", "/DF", "/DF")),
			)

		#-----------------------------------------------
		# ARITHMETIC OPERATIONS

		elif iw == 0xf4:
			# ADD     Add
			mne = "add"
			model += (
			    ("=", "/D",
				("+", "/D", ("MEM", "/R(X)", "#0b0", "/DF"))),
			)
		elif iw == 0xfc:
			# ADI b   Add Immediate
			mne = "adi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("+", "/D", "#0x%02x" % nw, "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
		elif iw == 0x74:
			# ADC     Add with Carry
			mne = "adc"
			model += (
			    ("=", "/D",
				("+", "/D", ("MEM", "/R(X)", "/DF", "/DF"))),
			)
		elif iw == 0x7c:
			# ADCI b  Add with Carry Immediate
			mne = "adci"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("+", "/D", "#0x%02x" % nw, "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)
		elif iw == 0xf5:
			# SD      Subtract D from memory
			mne = "sd"
			model += (
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)", "#0b0", "/DF"))),
			)
		elif iw == 0xfd:
			# SDI b   Subtract D from memory Immediate byte
			mne = "sdi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("-", "#0x%02x" % nw, "/D", "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
		elif iw == 0x75:
			# SDB     Subtract D from memory with Borrow
			mne = "sdb"
			model += (
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)", "/DF", "/DF"))),
			)
		elif iw == 0x7d:
			# SDBI b  Subtract D with Borrow, Immediate
			mne = "sdbi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("-", "#0x%02x" % nw, "/D", "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)
		elif iw == 0xf7:
			# SM      Subtract Memory from D
			mne = "sm"
			model += (
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)"), "#0b0", "/DF")),
			)
		elif iw == 0xff:
			# SMI b   Subtract Memory from D, Immediate
			mne = "smi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("-", "/D", "#0x%02x" % nw, "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
		elif iw == 0x77:
			# SMB     Subtract Memory from D with Borrow
			mne = "smb"
			model += (
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)"), "/DF", "/DF")),
			)
		elif iw == 0x7f:
			# SMBI b  Subtract Memory with Borrow, Immediate
			mne = "smbi"
			arg = "0x%02x" % nw
			length = 2
			model += (
			    ("=", "/D",
				("-", "/D", "#0x%02x" % nw, "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)

		#-----------------------------------------------
		# BRANCH INSTRUCTIONS - SHORT BRANCH

		elif ireg == 0x30:
			mne = ( "br",  "bq",  "bz",  "bdf",
				"b1",  "b2",  "b3",  "b4",
				"skp", "bnq", "bnz", "bnf",
				"bn1", "bn2", "bn3", "bn4") [nreg]
			length = 2
			da = (adr + 1 & 0xff00) | nw
			arg = "0x%04x" % da
			model += (
			    ("ZERO?", ("RND",),
				("INC", "/R(P)"),
			        ("=", "/R(P)", "#0x%04x" % da),
			    ),
			)
			if nreg == 0:
				# BR a    Branch unconditionally
				model = ("=", "/R(P)", "#0x%04x" % da)
				ins.flow = ("cond", "T", da )
			elif nreg == 1:
				# BQ a    Branch if Q is on
				# XXX: Does Q read different from /Q ?
				ins.flow("cond", "q", da )
				ins.flow("cond", "nq", adr + 2)
			elif nreg == 2:
				# BZ a    Branch on Zero
				model = ("SEQ",
				    ("INC", "/R(P)"),
				    ("ZERO?", "/D", 
					("=", "/R(P)", "#0x%04x" % da),
					("INC", "/R(P)"),
				    ),
				)
				ins.flow("cond", "Z", da )
				ins.flow("cond", "NZ", adr + 2)
			elif nreg == 3:
				# BDF a   Branch if DF is 1
				model = ("SEQ",
				    ("INC", "/R(P)"),
				    ("ZERO?", "/DF", 
					("INC", "/R(P)"),
					("=", "/R(P)", "#0x%04x" % da),
				    ),
				)
				ins.flow("cond", "DF", da )
				ins.flow("cond", "NDF", adr + 2)
			elif nreg >= 4 and nreg <= 7:
				# B1 a    Branch on External Flag 1
				# B2 a    Branch on External Flag 2
				# B3 a    Branch on External Flag 3
				# B4 a    Branch on External Flag 4
				ins.flow("cond", "b%d" % (nreg - 3), da )
				ins.flow("cond", "nb%d" % (nreg - 3), adr + 2)
			elif nreg == 8:
				# SKP     Skip one byte
				model = ("INC", "/R(P)", "#0x02")
				ins.flow("cond", "T", adr + 2 )
			elif nreg == 9:
				# BNQ a   Branch if Q is off
				ins.flow("cond", "nq", da )
				ins.flow("cond", "q", adr + 2)
			elif nreg == 0xa:
				# BNZ a   Branch on Not Zero
				model = ("SEQ",
				    ("INC", "/R(P)"),
				    ("ZERO?", "/D", 
					("INC", "/R(P)"),
					("=", "/R(P)", "#0x%04x" % da),
				    ),
				)
				ins.flow("cond", "NZ", da )
				ins.flow("cond", "Z", adr + 2)
			elif nreg == 0xb:
				# BNF a   Branch if DF is 0
				model = ("SEQ",
				    ("INC", "/R(P)"),
				    ("ZERO?", "/DF", 
					("=", "/R(P)", "#0x%04x" % da),
					("INC", "/R(P)"),
				    ),
				)
				ins.flow("cond", "NDF", da )
				ins.flow("cond", "DF", adr + 2)
			elif nreg >= 0xc and nreg <= 0xf:
				# BN1 a   Branch on Not External Flag 1
				# BN2 a   Branch on Not External Flag 2
				# BN3 a   Branch on Not External Flag 3
				# BN4 a   Branch on Not External Flag 4
				ins.flow("cond", "nb%d" % (nreg - 11), da )
				ins.flow("cond", "b%d" % (nreg - 11), adr + 2)

		#-----------------------------------------------
		# BRANCH INSTRUCTIONS - LONG BRANCH

		elif (iw & 0xf4) == 0xc0:
			da = p.m.b16(adr + 1)
			arg = "0x%04x" % da
			length = 3

			if iw == 0xc0:
				# LBR aa  Long Branch unconditionally
				mne = "lbr"
				model = ("=", "/R(P)", "#0x%04x" % da)
				ins.flow("cond", "T", da )
			elif iw == 0xc1:
				# LBQ aa  Long Branch if Q is on
				mne = "lbq"
				model = ("ZERO?", "/Q", 
					("=", "/R(P)", "#0x%04x" % da),
					("INC", "/R(P)", "#0x3"),
				)
				ins.flow("cond", "Q", da )
				ins.flow("cond", "NQ", adr + 3)
			elif iw == 0xc2:
				# LBZ aa  Long Branch if Zero
				mne = "lbz"
				model = ("ZERO?", "/D", 
					("=", "/R(P)", "#0x%04x" % da),
					("INC", "/R(P)", "#0x3"),
				)
				ins.flow("cond", "Z", da )
				ins.flow("cond", "NZ", adr + 3)
			elif iw == 0xc3:
				# LBDF aa Long Branch if DF is 1
				mne = "lbdf"
				model = ("ZERO?", "/DF", 
					("INC", "/R(P)", "#0x3"),
					("=", "/R(P)", "#0x%04x" % da),
				)
				ins.flow("cond", "DF", da )
				ins.flow("cond", "NDF", adr + 3)
			elif iw == 0xc8:
				# LSKP    Long Skip
				mne = "lskp"
				length = 1
				arg = None
				model = ("INC", "/R(P)", "#0x3")
				ins.flow("cond", "T", adr + 3 )
			elif iw == 0xc9:
				# LBNQ aa Long Branch if Q is off
				mne = "lbnq"
				model = ("ZERO?", "/Q", 
					("INC", "/R(P)", "#0x3"),
					("=", "/R(P)", "#0x%04x" % da),
				)
				ins.flow("cond", "NQ", da )
				ins.flow("cond", "Q", adr + 3)
			elif iw == 0xca:
				# LBNZ aa Long Branch if Not Zero
				mne = "lbnz"
				model = ("ZERO?", "/D", 
					("INC", "/R(P)", "#0x3"),
					("=", "/R(P)", "#0x%04x" % da),
				)
				ins.flow("cond", "NZ", da )
				ins.flow("cond", "Z", adr + 3)
			elif iw == 0xcb:
				# LBNF aa Long Branch if DF is 0
				mne = "lbnf"
				model = ("ZERO?", "/DF", 
					("=", "/R(P)", "#0x%04x" % da),
					("INC", "/R(P)", "#0x3"),
				)
				ins.flow("cond", "NDF", da )
				ins.flow("cond", "DF", adr + 3)
		#-----------------------------------------------
		# SKIP INSTRUCTIONS 

		# 0x38 and 0xc8: see above
		elif iw == 0xce:
			# LSZ    Long Skip if Zero
			mne = "lsz"
			model = ("ZERO?", "/D", 
			        ("INC", "/R(P)", "#0x3"),
			        ("INC", "/R(P)", "#0x1"),
			)
			ins.flow("cond", "NZ", adr + 1 )
			ins.flow("cond", "Z", adr + 3)
		elif iw == 0xc6:
			# LSNZ    Long Skip if Not Zero
			mne = "lsnz"
			model = ("ZERO?", "/D", 
			        ("INC", "/R(P)", "#0x1"),
			        ("INC", "/R(P)", "#0x3"),
			)
			ins.flow("cond", "Z", adr + 1 )
			ins.flow("cond", "NZ", adr + 3)
		elif iw == 0xcf:
			# LSDF    Long Skip if DF is 1
			mne = "lsdf"
			model = ("ZERO?", "/D", 
			        ("INC", "/R(P)", "#0x1"),
			        ("INC", "/R(P)", "#0x3"),
			)
			ins.flow("cond", "NDF", adr + 1 )
			ins.flow("cond", "DF", adr + 3)
		elif iw == 0xc7:
			# LSNF    Long Skip if DF is 0
			mne = "lsnf"
			model = ("ZERO?", "/DF", 
			        ("INC", "/R(P)", "#0x3"),
			        ("INC", "/R(P)", "#0x1"),
			)
			ins.flow("cond", "DF", adr + 1 )
			ins.flow("cond", "NDF", adr + 3)

		elif iw == 0xcd:
			# LSQ     Long Skip if Q is on
			mne = "lsq"
			model = ("ZERO?", "/Q", 
			        ("INC", "/R(P)", "#0x1"),
			        ("INC", "/R(P)", "#0x3"),
			)
			ins.flow("cond", "NQ", adr + 1 )
			ins.flow("cond", "Q", adr + 3)
		elif iw == 0xc5:
			# LSNQ    Long Skip if Q is off
			mne = "lsnq"
			model = ("ZERO?", "/Q", 
			        ("INC", "/R(P)", "#0x3"),
			        ("INC", "/R(P)", "#0x1"),
			)
			ins.flow("cond", "Q", adr + 1 )
			ins.flow("cond", "NQ", adr + 3)
		elif iw == 0xcc:
			# LSIE    Long Skip if Interrupts Enabled
			mne = "lsie"
			model = ("ZERO?", "/IE", 
			        ("INC", "/R(P)", "#0x1"),
			        ("INC", "/R(P)", "#0x3"),
			)
			ins.flow("cond", "NIE", adr + 1 )
			ins.flow("cond", "IE", adr + 3)

		#-----------------------------------------------
		# CONTROL INSTRUCTIONS 

		elif iw == 0x00:
			# IDL     Idle
			mne = "idl"
			model = ("INC", "/R(P)")
		elif iw == 0xc4:
			# NOP     No Operation
			mne = "nop"
			model = ("INC", "/R(P)")
		elif ireg == 0xd0:
			# SEP r   Set P
			mne = "sep"
			arg = "%d" % nreg
			model += ( ("=", "/P", "#0x%x" % nreg), )
		elif ireg == 0xe0:
			# SEX r   Set X
			mne = "sex"
			arg = "%d" % nreg
			model += ( ("=", "/X", "#0x%x" % nreg), )
		elif iw == 0x7b:
			# SEQ     Set Q
			mne = "seq"
			model += ( ("=", "/Q", "#0b1"), )
		elif iw == 0x7a:
			# REQ     Reset Q
			mne = "req"
			model += ( ("=", "/Q", "#0b0"), )
		elif iw == 0x78:
			# SAV     Save T
			mne = "sav"
			model += ( ("MEM", "/R(X)", "/T"), )
		elif iw == 0x79:
			# MARK    Save X and P in T
			# XXX: untested
			mne = "mark"
			model += (
			    ("=", "/T", ("OR", "/P", ("<<", "/T", "#0x04"))),
			    ("MEM", "/R2", "/T")
			    ("DEC", "/R2")
		        )
		elif iw == 0x70 or iw == 0x71:
			# RET     Return
			# DIS     Return and Disable Interrupts
			if iw == 0x70:
				mne = "ret"
			else:
				mne = "dis"
			model += (
			    ("=", "/P", ("TRIM", ("MEM", "/R(X)"), "#0x4")),
			    ("=", "/X", ("TRIM",
				(">>", ("MEM", "/R(X)"), "#0x4"),
				"#0x4")),
			    ("INC", "/R(X)"),
			    ("=", "/IE", "#0b%d" % (1^(iw & 1))),
			)

		#------------------------------------------
		# INPUT - OUTPUT BYTE TRANSFER

		elif ireg == 0x60 and nreg >= 1 and nreg <= 7:
			# OUT p   Output from memory (for p = 1 to 7)
			mne = "out"
			arg = "%d" % nreg
			model += (
			    ("BUS", "#0x%x" % nreg, ("MEM", "/R(X)")),
			    ("INC", "/R(X)"),
			)
		elif ireg == 0x60 and nreg >= 9 and nreg <= 0xf:
			# INP p   Input to memory and D (for p = 9 to F)
			mne = "in"
			arg = "%d" % (nreg & 7)
			model += (
			    ("MEM", "/R(X)", ("BUS", "#0x%x" % (nreg & 7))),
			)

		#------------------------------------------
		# Not matched:  bug ?

		else:
			print("cdp1802.disass(0x%x, " % adr, ") = 0x%02x" % iw)
			ins.fail("no instruction")
			return

		#print("%04x" % adr, "%02x" % iw, mne, arg, flow)
		ins.mne = mne
		ins.hi = ins.lo + length
		if arg != None:
			ins.oper.append(arg)

		if state == None:
			state = copy.deepcopy(unknown_state)
			state['/P'] = (4, 3)
			state['/R3.0'] = (8, adr & 0xff)
			state['/R3.1'] = (8, adr >> 8)
		if False and model != None:
			x.a['model'] = model
			x.cmt.append(str(model))
			x.cmt.append(self.model.render_state(state))
			self.model.eval(p, state, model)
			v = self.model.getreg(p, state, "/R(P)")
			if v[1] != None:
				#print("--> Model %04x %04x" % (adr, v[1]))
				p.todo(v[1], p.cpu.disass, copy.deepcopy(state))
