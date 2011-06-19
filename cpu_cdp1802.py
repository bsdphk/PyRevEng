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

inscode = (
	"1idle", "rldn",  "rldn",  "rldn",  "rldn",  "rldn",  "rldn",  "rldn", 
	"rldn",  "rldn",  "rldn",  "rldn",  "rldn",  "rldn",  "rldn",  "rldn", 

	"rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc", 
	"rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc",  "rinc", 

	"rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec", 
	"rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec",  "rdec", 

	"Abr",   "abq",   "abz",   "abdf",  "ab1",   "ab2",   "ab3",   "ab4",  
	"-????", "abnq",  "abnz",  "abnf",  "abn1",  "abn2",  "abn3",  "abn4", 


	"rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda", 
	"rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda",  "rlda", 

	"rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr", 
	"rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr",  "rstr", 

	"1irx",  "pout",  "pout",  "pout",  "pout",  "pout",  "pout",  "pout", 
	"-????", "pin",   "pin",   "pin",   "pin",   "pin",   "pin",   "pin",  

	"1ret",  "1dis",  "1ldxa", "1stxd", "1adc",  "1sdb",  "1shrc", "1smb", 
	"-????", "-????", "1req",  "1seq",  "sadci", "ssdbi", "1shlc", "ssmbi",


	"rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo", 
	"rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo",  "rglo", 

	"rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi", 
	"rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi",  "rghi", 

	"rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo", 
	"rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo",  "rplo", 

	"rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi", 
	"rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi",  "rphi", 


	"Clbr",  "clbq",  "clbz",  "clbdf", "1nop",  "llsnq", "llsnz", "llsnf", 
	"Llskp", "clbnq", "clbnz", "clbnf", "llsie", "llsq",  "llsz",  "llsdf",

	"rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep", 
	"rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep",  "rsep", 

	"rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex", 
	"rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex",  "rsex", 

	"1ldx",  "1or",   "1and",  "1xor",  "1add",  "1sd",   "1shr",  "1sm",  
	"bldi",  "bori",  "bani",  "bxri",  "badi",  "bsdi",  "1shl",  "bsmi",
)

class cdp1802(object):
	def __init__(self):
		assert len(inscode) == 256
		for i in range(0,256):
			if inscode[i] == "-????":
				print("Missing ins %02x" % i)
		self.dummy = True

	def vectors(self, p):
		r = ("R0",)
		p.todo(0, self.disass, r)

	def render(self, p, t, lvl):
		s = t.a['mne']
		if t.a['arg'] != None:
			s += "\t" + t.a['arg']
		return (s,)

	def ins(self, p, adr, length, state, mne, arg = None, flow = None):
		print("%04x" % adr, mne, arg, flow)
		x = p.t.add(adr, adr + length, "ins")
		x.render = self.render
		x.a['mne'] = mne
		x.a['arg'] = arg
		x.a['state'] = state
		if flow != None:
			x.a['flow'] = flow
		p.ins(x, self.disass)

	def disass(self, p, adr, state):

		try:
			iw = p.m.rd(adr)
			nw = p.m.rd(adr + 1)
		except:
			print("NOMEM cdp1802.disass(0x%x, " % adr, state, ")")
			return

		n = iw & 0x0f
		ic = inscode[iw]
		#print("cdp1802.disass(0x%x, " % adr, state, ") = 0x%02x" % iw, ic)

		if iw == 0xd4:	
			# XXX: hack
			da = p.m.b16(adr + 1)
			self.ins(p, adr, 3, state, "xcall", "0x%04x" % da,
			    (
				("call", "T", da),
			    )
			)
		elif iw == 0xd5:	
			# XXX: hack
			self.ins(p, adr, 1, state, "xret", None,
			    (
				("ret", "T", None),
			    )
			)
			
	
		elif ic[0] == "1":
			self.ins(p, adr, 1, state, ic[1:])
		elif ic[0] == "A":
			# short branch uncond
			self.ins(p, adr, 2, state, ic[1:], "0x%02x" % nw,
			    (
				("cond", "T", adr & 0xff00 | nw, ),
			    )
			)
		elif ic[0] == "a":
			# short branch
			self.ins(p, adr, 2, state, ic[1:], "0x%02x" % nw,
			    (
				("cond", "X", adr + 2),
				("cond", "X", adr & 0xff00 | nw)
			    )
			)
		elif ic[0] == "C":
			# long branch uncond
			da = p.m.b16(adr + 1)
			self.ins(p, adr, 3, state, ic[1:], "0x%04x" % da,
			    (
				("cond", "T", da),
			    )
			)
		elif ic[0] == "c":
			# long branch
			da = p.m.b16(adr + 1)
			self.ins(p, adr, 3, state, ic[1:], "0x%04x" % da,
			    (
				("cond", "X", adr + 3),
				("cond", "X", da),
			    )
			)
		elif ic[0] == "b":
			self.ins(p, adr, 2, state, ic[1:], "0x%02x" % nw)
		elif ic[0] == "l":
			# long skip
			self.ins(p, adr, 1, state, ic[1:], None,
			    (
				("cond", "X", adr + 1),
				("cond", "X", adr + 3),
			    )
			)
		elif ic[0] == "L":
			# Uncondition long skip
			self.ins(p, adr, 1, state, ic[1:], None,
			    (
				("cond", "T", adr + 3),
			    )
			)
		elif ic[0] == "p":
			self.ins(p, adr, 1, state, ic[1:], "%d" % (n & 7))
		elif ic[0] == "r":
			self.ins(p, adr, 1, state, ic[1:], "%d" % n)
		elif ic[0] == "s":
			# signed imm
			self.ins(p, adr, 2, state, ic[1:], "%d" % p.m.s8(adr + 1))
		elif True:
			print("cdp1802.disass(0x%x, " % adr, state, ") = 0x%02x" % iw, ic)
	
