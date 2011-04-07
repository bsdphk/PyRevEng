#!/usr/local/bin/python
#

from __future__ import print_function

import cpu_nova

class domus(cpu_nova.nova):
	def __init__(self):
		cpu_nova.nova.__init__(self)
		self.special = dict()
		self.special[0o006002] = (
			"WAIT",
			(
				"     Call    Return   Error",
				"             ans/msg  t'out/irq",
				"AC0  delay   first    unchg",
				"AC1  device  second   device",
				"AC2  buf     nextbuf  cur",
				"AC3  link    cur      cur"
			), (
				"TIMEOUT",
				"INTERRUPT",
				"ANSWER",
				"MESSAGE"
			)
		)
		self.special[0o006003] = (
			"WAITINTERRUPT",
			(
				"     Call    Return",
				"AC0  -       unchg",
				"AC1  device  device",
				"AC2  delay   cur",
				"AC3  link    cur",
			), (
				"TIMEOUT",
				"INTERRUPT"
			)
		)
		self.special[0o006004] = (
			"SENDMESSAGE",
			(
				"     Call    Return Error",
				"AC0  -       unchg  unchg",
				"AC1  address adress adress",
				"AC2  nameadr buf    error",
				"AC3  link    cur    cur"
			),
		)
		self.special[0o006005] = (
			"WAITANSWER",
			(
				"     Call    Return",
				"AC0  -       first",
				"AC1  -       second",
				"AC2  buf     buf",
				"AC3  link    cur",
			)
		)
		self.special[0o006006] = (
			"WAITEEVENT",
			(
				"     Call    Return",
				"AC0  -       first",
				"AC1  -       second",
				"AC2  buf     next buf",
				"AC3  link    cur",
			), (
				"ANSWER",
				"MESSAGE"
			)
		)
		self.special[0o006007] = ( "SENDANSWER",)
		self.special[0o006010] = ( "SEARCHITEM",)
		self.special[0o006011] = ( "CLEANPROCESS",)
		self.special[0o006012] = ( "BREAKPROCESS",)
		self.special[0o006013] = ( "STOPPROCESS",)
		self.special[0o006014] = ( "STARTPROCESS",)
		self.special[0o006015] = ( "RECHAIN",)
		self.special[0o006164] = ( "NEXTOPERATION", (), ("CONTROL", "INPUT", "OUTPUT"))
		self.special[0o006165] = ( "RETURANSWER",)
		self.special[0o006167] = ( "WAITOPERATION", (), ("TIMER", "INTERRUPT", "ANSWER", "CONTROL", "INPUT", "OUTPUT"))
		self.special[0o006170] = ( "SETINTERRUPT",)
		self.special[0o006171] = ( "SETRESERVATION",)
		self.special[0o006172] = ( "SETCONVERSION",)
		self.special[0o006173] = ( "CONBYTE",)
		self.special[0o006174] = ( "GETBYTE",)
		self.special[0o006175] = ( "PUTBYTE",)
		self.special[0o006176] = ( "MULTIPLY",)

		self.special[0o006232] = ( "BINDEC",)
		self.special[0o006233] = ( "DECBIN",)
		self.special[0o006200] = ( "GETREC",)
		self.special[0o006201] = ( "PUTREC",)
		self.special[0o006202] = ( "WAITTRANSFER",)
		self.special[0o006204] = ( "TRANSFER",)
		self.special[0o006205] = ( "INBLOCK",)
		self.special[0o006206] = ( "OUTBLOCK",)
		self.special[0o006207] = ( "INCHAR",)
		self.special[0o006210] = ( "FREESHARE",)
		self.special[0o006211] = ( "OUTSPACE",)
		self.special[0o006212] = ( "OUTCHAR",)
		self.special[0o006213] = ( "OUTNL",)
		self.special[0o006214] = ( "OUTEND",)
		self.special[0o006215] = ( "OUTTEXT",)
		self.special[0o006216] = ( "OUTOCTAL",)
		self.special[0o006217] = ( "SETPOSITION",)
		self.special[0o006220] = ( "CLOSE",)
		self.special[0o006221] = ( "OPEN",)
		self.special[0o006223] = ( "INNAME",)
		self.special[0o006222] = ( "WAITZONE",)
		self.special[0o006224] = ( "MOVE",)
		self.special[0o006225] = ( "INTERPRETE",)

		self.special[0o006334] = ( "CDELAY",)
		self.special[0o006335] = ( "WAITSE",)
		self.special[0o006336] = ( "WAITCH",)
		self.special[0o006337] = ( "CWANSW",)
		self.special[0o006340] = ( "CTEST",)
		self.special[0o006341] = ( "CPRINT",)
		self.special[0o006343] = ( "CTOUT",)
		self.special[0o006343] = ( "SIGNAL",)
		self.special[0o006344] = ( "SIGCH",)
		self.special[0o006345] = ( "CPASS",)

		self.special[0o006346] = ( "CREATEENTRY",)
		self.special[0o006347] = ( "LOOKUPENTRY",)
		self.special[0o006350] = ( "CHANGEENTRY",)
		self.special[0o006351] = ( "REMOVEENTRY",)
		self.special[0o006352] = ( "INITCATALOG",)
		self.special[0o006353] = ( "SETENTRY",)
	
		self.special[0o006354] = (
			"COMON",
			(
				"     Call    @Dest",
				"AC0  -       unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    corout",
			), (	
				None,
				"RETURN"
			)
		
		)
		self.special[0o006355] = (
			"CALL",
			(	
				"     Call    @Dest",
				"AC0  -       unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    link+1",
			), (	
				None,
				"RETURN"
			)
		)
		self.special[0o006356] = (
			"GOTO",
			(	
				"     Call    @Dest",
				"AC0  -       unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    destr",
			), (	
				None,
			)
		)
		self.special[0o006357] = (
			"GETADR",
			(
				"     Call    return",
				"AC0  point   unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    address",
			)
		)
		self.special[0o006360] = (
			"GETPOINT",
			(
				"     Call    return",
				"AC0  address unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    point",
			)
		)

		self.special[0o006364] = ( "CSENDM",)
		self.special[0o006365] = ( "SIGGEN",)
		self.special[0o006366] = ( "WAITGE",)
		self.special[0o006367] = ( "CTOP",)

		self.special[0o006177] = ( "DIVIDE",)

	def disass(self, p, adr, priv = None):
		try:
			q = p.m.rdqual(adr)
			if q != 1:
				return
		except:
			pass
		try:
			iw = p.m.rd(adr)
		except:
			return
		if iw not in self.special:
			cpu_nova.nova.disass(self, p,adr,priv)
			return
		x = p.t.add(adr, adr + 1, "ins")
		ss = self.special[iw]
		x.a['mne'] = ss[0]
		x.a['oper'] = list()
		x.render = self.render

		if len(ss) > 1 and ss[1] != -1:
			x.cmt += ss[1]
		if len(ss) > 2:
			assert len(ss[2]) > 0
			for i in ss[2]:
				adr += 1
				if i != None:
					if not 'cond' in x.a:
						x.a['cond'] = list()
					x.a['cond'].append((i, adr))
					p.todo(adr, self.disass)

		p.ins(x, self.disass)

