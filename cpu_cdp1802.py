#!/usr/local/bin/python3.2

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
	
