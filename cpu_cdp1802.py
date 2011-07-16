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

class model_cdp1802(model.model):
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
		


class cdp1802(object):
	def __init__(self):
		self.model = model_cdp1802()

	def vectors(self, p):
		ss = copy.deepcopy(unknown_state)
		for i in reset_state:
			ss[i] = reset_state[i]
		p.todo(0, self.disass, ss)

	def render(self, p, t, lvl):
		s = t.a['mne']
		if t.a['arg'] != None:
			s += "\t" + t.a['arg']
		return (s,)

	def ins(self, p, adr, length, mne, arg = None, flow = None, model = None, state = None):
		# print("%04x" % adr, mne, arg, flow)
		x = p.t.add(adr, adr + length, "ins")
		x.render = self.render
		x.a['mne'] = mne
		x.a['arg'] = arg
		if state == None:
			state = copy.deepcopy(unknown_state)
			state['/P'] = (4, 3)
			state['/R3.0'] = (8, adr & 0xff)
			state['/R3.1'] = (8, adr >> 8)
		if model != None:
			x.a['model'] = model
			x.cmt.append(str(model))
			x.cmt.append(self.model.render_state(state))
			self.model.eval(p, state, model)
			v = self.model.getreg(p, state, "/R(P)")
			if v[1] != None:
				p.todo(v[1], p.cpu.disass, copy.deepcopy(state))
		if flow != None:
			x.a['flow'] = flow
		p.ins(x, self.disass)

	def disass(self, p, adr, priv = None):
		#print("cdp1802.disass(0x%x, " % adr, priv, ")")
		if p.t.find(adr, "ins") != None:
			return

		try:
			iw = p.m.rd(adr)
			nw = p.m.rd(adr + 1)
		except:
			print("NOMEM cdp1802.disass(0x%x, " % adr, ")")
			return

		ireg = iw & 0xf0
		nreg = iw & 0x0f

		model = None

		if iw == 0xd4:	
			# XXX: hack
			da = p.m.b16(adr + 1)
			self.ins(p, adr, 3, "xcall", "0x%04x" % da,
			    (
				("call", "T", da),
			    ), model = model
			)
		elif iw == 0xd5:	
			# XXX: hack
			self.ins(p, adr, 1, "xret", None,
			    (
				("ret", "T", None),
			    ), model = model
			)

		elif iw == 0x00:
			# IDL -- Wait for IRQ/DMA -- 
			model = ("INC", "/R(P)")
			self.ins(p, adr, 1, "idl", model = model, state=priv)
		elif ireg == 0x00:
			# LDN -- Load via N -- D = M(R(N))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("MEM", "/R%d" % nreg)),
			)
			self.ins(p, adr, 1, "ldn", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0x10:
			# INC -- Increment -- R(N) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("INC", "/R%d" % nreg),
			)
			self.ins(p, adr, 1, "inc", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0x20:
			# DEC -- Decrement -- R(N) -= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("DEC", "/R%d" % nreg),
			)
			self.ins(p, adr, 1, "dec", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0x30 and nreg & 4:
			# B1-B4,BN1-BN4 -- Short Branch in inputs
			da = adr + 1 & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("RND",
				("INC", "/R(P)"),
			        ("=", "/R(P)", "#0x%04x" % da),
			    ),
			)
			s = "b"
			if nreg >= 8:
				s += "n"
			s += "%d" % ((nreg & 3) + 1)
			self.ins(p, adr, 2, s, "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", s, da ),
				("cond", "n" + s, adr + 2),
			    ))
		elif iw == 0x30:
			# BR -- Short Branch
			da = (adr + 1) & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/R(P)", "#0x%04x" % da),
			)
			self.ins(p, adr, 2, "br", "0x%04x" % da,
			    model = model, state=priv,
			    flow = ( ("cond", "T", da ),)
			    )
		elif iw == 0x32:
			# BZ -- Short Branch if not D
			da = (adr + 1) & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("ZERO?", "/D", 
			        ("=", "/R(P)", "#0x%04x" % da),
			        ("INC", "/R(P)"),
			    ),
			)
			self.ins(p, adr, 2, "bz", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "Z", da ),
				("cond", "NZ", adr + 2),
			    ))
		elif iw == 0x33:
			# BDF -- Short Branch if DF
			da = (adr + 1) & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("ZERO?", "/DF", 
			        ("=", "/R(P)", "#0x%04x" % da),
			        ("INC", "/R(P)"),
			    ),
			)
			self.ins(p, adr, 2, "bdf", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "DF", da ),
				("cond", "NDF", adr + 2),
			    ))
		elif iw == 0x3a:
			# BNZ -- Short Branch
			da = (adr + 1) & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("ZERO?", "/D", 
			        ("INC", "/R(P)"),
			        ("=", "/R(P)", "#0x%04x" % da),
			    ),
			)
			self.ins(p, adr, 2, "bnz", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "NZ", da ),
				("cond", "Z", adr + 2),
			    ))
		elif iw == 0x3b:
			# BDF -- Short Branch if not DF
			da = (adr + 1) & 0xff00
			da |= nw
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("ZERO?", "/DF", 
			        ("INC", "/R(P)"),
			        ("=", "/R(P)", "#0x%04x" % da),
			    ),
			)
			self.ins(p, adr, 2, "bdnf", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "NDF", da ),
				("cond", "DF", adr + 2),
			    ))
		elif ireg == 0x40:
			# LDA -- Load Advance -- D = M(R(N)); R(N) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("MEM", "/R%d" % nreg)),
			    ("INC", "/R%d" % nreg),
			)
			self.ins(p, adr, 1, "lda", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0x50:
			# STR -- Store -- M(R(N)) = D
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("MEM", "/R%d" % nreg, "/D"),
			)
			self.ins(p, adr, 1, "str", "%d" % nreg,
			    model = model, state=priv)
		elif iw == 0x60:
			# IRX -- Increment X
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("INC", "/X"),
			)
			self.ins(p, adr, 1, "irx", model = model, state=priv)
		elif ireg == 0x60 and nreg < 8:
			# OUT -- OUTPUT -- BUS = M(R(X)); R(X) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("BUS", "#0x%x" % nreg, ("MEM", "/R(X)")),
			    ("INC", "/R(X)"),
			)
			self.ins(p, adr, 1, "out", "%d" % nreg,
			    flow=(), model = model, state=priv)
		elif ireg == 0x60 and nreg > 7:
			# IN -- Input -- M(R(X)) = BUS
			nreg &= 7
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("MEM", "/R(X)", ("BUS", "#0x%x" % (nreg % 7))),
			)
			self.ins(p, adr, 1, "in", "%d" % (nreg & 7),
			    model = model, state=priv)
		elif iw == 0x70:
			# RET -- Disable interrupt -- X,P = M(R(X)); R(X)+=1, IE = 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/P", ("TRIM", ("MEM", "/R(X)"), "#0x4")),
			    ("=", "/X", ("TRIM", (">>", ("MEM", "/R(X)"), "#0x4"), "#0x4")),
			    ("INC", "/R(X)"),
			    ("=", "/IE", "#0b1"),
			)
			self.ins(p, adr, 1, "ret", model = model, state=priv)
		elif iw == 0x71:
			# DIS -- Disable interrupt -- X,P = M(R(X)); R(X)+=1, IE = 0
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/P", ("TRIM", ("MEM", "/R(X)"), "#0x4")),
			    ("=", "/X", ("TRIM", (">>", ("MEM", "/R(X)"), "#0x4"), "#0x4")),
			    ("INC", "/R(X)"),
			    ("=", "/IE", "#0b0"),
			)
			self.ins(p, adr, 1, "dis",
			    flow = (), model = model, state=priv)
		elif iw == 0x72:
			# LDXA -- Load via X and increment -- D = M(R(X)); R(X) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("MEM", "/R(X)")),
			    ("INC", "/R(X)"),
			)
			self.ins(p, adr, 1, "ldxa", model = model, state=priv)
		elif iw == 0x73:
			# STXD -- Store via X and decrement -- M(R(X)) = D; R(X) -= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("MEM", "/R(X)", "/D"),
			    ("DEC", "/R(X)"),
			)
			self.ins(p, adr, 1, "stxd", model = model, state=priv)
		elif iw == 0x74:
			# ADC -- Add w/cy -- D,DF += M(R(X)) + DF
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("+", "/D", ("MEM", "/R(X)", "/DF", "/DF"))),
			)
			self.ins(p, adr, 1, "adc", model = model, state=priv)
		elif iw == 0x7c:
			# ADCI -- Add w/CY Immediate -- D,DF += M(R(P)) + DF; R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("+", "/D", "#0x%02x" % nw, "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "adci", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0x76:
			# SHRC -- Shift Right w/cy -- DF,D,DF <<= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", (">>", "/D", "#0x0", "/DF", "/DF")),
			)
			self.ins(p, adr, 1, "shrc", model = model, state=priv)
		elif iw == 0x77:
			# SMB -- Subtract Memory w/borrow
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)"), "/DF", "/DF")),
			)
			self.ins(p, adr, 1, "smb", model = model, state=priv)
		elif iw == 0x7a:
			# REQ -- Reset Q
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/Q", "#0b0"),
			)
			self.ins(p, adr, 1, "req", model = model, state=priv)
		elif iw == 0x7b:
			# SEQ -- Set Q
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/Q", "#0b1"),
			)
			self.ins(p, adr, 1, "seq", model = model, state=priv)
		elif iw == 0x7d:
			# SDBI -- Sub D w/b Immediate -- DF,D -= M(R(P)) + DF; R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "#0x%02x" % nw, "/D", "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "sdbi", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0x7e:
			# SHLC -- Shift Left w/cy -- DF,D,DF <<= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("<<", "/D", "#0x0", "/DF", "/DF")),
			)
			self.ins(p, adr, 1, "shlc", model = model, state=priv)
		elif iw == 0x7f:
			# SMBI -- Sub w/b Immediate -- DF,D -= M(R(P)) + DF; R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "/D", "#0x%02x" % nw, "/DF", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "smbi", "0x%02x" % nw,
			    model = model, state=priv)
		elif ireg == 0x80:
			# GLO -- Get Low -- D = R(N).0
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", "/R%d.0" % nreg),
			)
			self.ins(p, adr, 1, "glo", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0x90:
			# GHI -- Get High -- D = R(N).1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", "/R%d.1" % nreg),
			)
			self.ins(p, adr, 1, "ghi", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0xa0:
			# PLO -- Put Low -- R(N).0 = D
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/R%d.0" % nreg, "/D"),
			)
			self.ins(p, adr, 1, "plo", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0xb0:
			# PHI -- Put High -- R(N).1 = D
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/R%d.1" % nreg, "/D"),
			)
			self.ins(p, adr, 1, "phi", "%d" % nreg,
			    model = model, state=priv)
		elif iw == 0xc0:
			# LBR -- Long Branch 
			da = p.m.b16(adr + 1)
			model = ("=", "/R(P)", "#0x%04x" % da)
			self.ins(p, adr, 3, "lbr", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "T", da ),
			    )
			)
		elif iw == 0xc2:
			# LBZ -- Long Branch if not D
			da = p.m.b16(adr + 1)
			model = (
			    "ZERO?", "/D", 
				("=", "/R(P)", "#0x%04x" % da),
			        ("INC", "/R(P)", "#0x3"),
			)
			self.ins(p, adr, 3, "lbdf", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "Z", da ),
				("cond", "NZ", adr + 3),
			    )
			)
		elif iw == 0xc3:
			# LBDF -- Long Branch if DF 
			da = p.m.b16(adr + 1)
			model = (
			    "ZERO?", "/DF", 
			        ("INC", "/R(P)", "#0x3"),
				("=", "/R(P)", "#0x%04x" % da),
		        )
			self.ins(p, adr, 3, "lbdf", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "DF", da ),
				("cond", "NDF", adr + 3),
			    )
			)
		elif iw == 0xc6:
			# LSNZ -- Long skip if D
			model = (
			    "ZERO?", "/D", 
			        ("INC", "/R(P)", "#0x3"),
			        ("INC", "/R(P)", "#0x1"),
			    )
			self.ins(p, adr, 1, "lsnz",
			    model = model, state=priv,
			    flow = (
				("cond", "Z", adr + 1 ),
				("cond", "NZ", adr + 3),
			    )
			)
		elif iw == 0xc8:
			# LSKP -- Long Skip -- R(P) += 2
			model = ("INC", "/R(P)", "#0x3")
			self.ins(p, adr, 1, "lskp", 
			    model = model, state=priv,
			    flow = (("cond", "T", adr + 3),)
			)
		elif iw == 0xca:
			# LBNZ -- Long Branch if D
			da = p.m.b16(adr + 1)
			model = (
			    "ZERO?", "/D", 
				("=", "/R(P)", "#0x%04x" % da),
			        ("INC", "/R(P)", "#0x3"),
			)
			self.ins(p, adr, 3, "lbnz", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "NZ", da ),
				("cond", "Z", adr + 3),
			    )
			)
		elif iw == 0xcb:
			# LBDF -- Long Branch if not DF 
			da = p.m.b16(adr + 1)
			model = (
			    "ZERO?", "/DF", 
				("=", "/R(P)", "#0x%04x" % da),
			        ("INC", "/R(P)", "#0x3"),
			)
			self.ins(p, adr, 3, "lbnf", "0x%04x" % da,
			    model = model, state=priv,
			    flow = (
				("cond", "NDF", da ),
				("cond", "DF", adr + 3),
			    )
			)
		elif ireg == 0xd0:
			# SEP -- Set P -- P = N
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/P", "#0x%x" % nreg),
			)
			self.ins(p, adr, 1, "sep", "%d" % nreg,
			    model = model, state=priv)
		elif ireg == 0xe0:
			# SEX -- Set X -- X = N
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/X", "#0x%x" % nreg),
			)
			self.ins(p, adr, 1, "sex", "%d" % nreg,
			    model = model, state=priv)
		elif iw == 0xf0:
			# LDX -- Load by X -- D = M(R(X))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("MEM", "/R(X)")),
			)
			self.ins(p, adr, 1, "ldx", model = model, state=priv)
		elif iw == 0xf1:
			# OR -- OR -- D |= M(R(X))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("OR", "/D", ("MEM", "/R(X)"))),
			)
			self.ins(p, adr, 1, "or", model = model, state=priv)
		elif iw == 0xf2:
			# AND -- AND -- D &= M(R(X))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("AND", "/D", ("MEM", "/R(X)"))),
			)
			self.ins(p, adr, 1, "and", model = model, state=priv)
		elif iw == 0xf3:
			# XOR -- Exclusive Or -- D ^= M(R(X))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("XOR", "/D", ("MEM", "/R(X)"))),
			)
			self.ins(p, adr, 1, "xor", model = model, state=priv)
		elif iw == 0xf4:
			# ADD -- Add -- D,DF += M(R(X))
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("+", "/D", ("MEM", "/R(X)", "#0b0", "/DF"))),
			)
			self.ins(p, adr, 1, "add", model = model, state=priv)
		elif iw == 0xf6:
			# SHR -- Shift Right -- D <<= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", (">>", "/D", "#0x0", "#0b0", "/DF")),
			)
			self.ins(p, adr, 1, "shr", model = model, state=priv)
		elif iw == 0xf7:
			# SM -- Subtract Memory
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "/D", ("MEM", "/R(X)"), "#0b0", "/DF")),
			)
			self.ins(p, adr, 1, "sm", model = model, state=priv)
		elif iw == 0xf8:
			# LDI -- Load Immediate -- D = M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", "#0x%02x" % nw),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "ldi", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xf9:
			# ORI -- OR Immediate -- D |= M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("OR", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "ori", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xfa:
			# ANI -- And Immediate -- D &= M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("AND", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "ani", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xfb:
			# XRI -- Xor Immediate -- D ^= M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("XOR", "/D", "#0x%02x" % nw)),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "xri", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xfc:
			# ADI -- Add Immediate -- D,DF += M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("+", "/D", "#0x%02x" % nw, "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "adi", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xfd:
			# SDI -- Sub D Immediate -- DF,D -= M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "#0x%02x" % nw, "/D", "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "sdi", "0x%02x" % nw,
			    model = model, state=priv)
		elif iw == 0xfe:
			# SHL -- Shift Left -- D <<= 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D", ("<<", "/D", "#0x0", "#0b0", "/DF")),
			)
			self.ins(p, adr, 1, "shl", model = model, state=priv)
		elif iw == 0xff:
			# SMI -- Sub Immediate -- DF,D -= M(R(P)); R(P) += 1
			model = ("SEQ",
			    ("INC", "/R(P)"),
			    ("=", "/D",
				("-", "/D", "#0x%02x" % nw, "#0b0", "/DF")),
			    ("INC", "/R(P)"),
			)
			self.ins(p, adr, 2, "smi", "0x%02x" % nw,
			    model = model, state=priv)
		elif True:
			print("cdp1802.disass(0x%x, " % adr, ") = 0x%02x" % iw)
	
