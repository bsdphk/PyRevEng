#!/usr/local/bin/python
#

from __future__ import print_function

import cpu_nova

class domus(cpu_nova.nova):
	def __init__(self):
		cpu_nova.nova.__init__(self)
		self.special = dict()
		self.special[006002] = (
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
		self.special[006003] = (
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
		self.special[006004] = (
			"SENDMESSAGE",
			(
				"     Call    Return Error",
				"AC0  -       unchg  unchg",
				"AC1  address adress adress",
				"AC2  nameadr buf    error",
				"AC3  link    cur    cur"
			),
		)
		self.special[006005] = (
			"WAITANSWER",
			(
				"     Call    Return",
				"AC0  -       first",
				"AC1  -       second",
				"AC2  buf     buf",
				"AC3  link    cur",
			)
		)
		self.special[006006] = (
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
		self.special[006007] = ( "SENDANSWER")
		self.special[006010] = ( "SEARCHITEM")
		self.special[006011] = ( "CLEANPROCESS")
		self.special[006012] = ( "BREAKPROCESS")
		self.special[006013] = ( "STOPPROCESS")
		self.special[006014] = ( "STARTPROCESS")
		self.special[006015] = ( "RECHAIN")
		self.special[006164] = ( "NEXTOPERATION", (), ("CONTROL", "INPUT", "OUTPUT"))
		self.special[006165] = ( "RETURANSWER")
		self.special[006167] = ( "WAITOPERATION", (), ("TIMER", "INTERRUPT", "ANSWER", "CONTROL", "INPUT", "OUTPUT"))
		self.special[006170] = ( "SETINTERRUPT")
		self.special[006171] = ( "SETRESERVATION")
		self.special[006172] = ( "SETCONVERSION")
		self.special[006173] = ( "CONBYTE")
		self.special[006174] = ( "GETBYTE")
		self.special[006175] = ( "PUTBYTE")
		self.special[006176] = ( "MULTIPLY")

		self.special[006232] = ( "BINDEC")
		self.special[006233] = ( "DECBIN")
		self.special[006200] = ( "GETREC")
		self.special[006201] = ( "PUTREC")
		self.special[006202] = ( "WAITTRANSFER")
		self.special[006204] = ( "TRANSFER")
		self.special[006205] = ( "INBLOCK")
		self.special[006206] = ( "OUTBLOCK")
		self.special[006207] = ( "INCHAR")
		self.special[006210] = ( "FREESHARE")
		self.special[006211] = ( "OUTSPACE")
		self.special[006212] = ( "OUTCHAR")
		self.special[006213] = ( "OUTNL")
		self.special[006214] = ( "OUTEND")
		self.special[006215] = ( "OUTTEXT")
		self.special[006216] = ( "OUTOCTAL")
		self.special[006217] = ( "SETPOSITION")
		self.special[006220] = ( "CLOSE")
		self.special[006221] = ( "OPEN")
		self.special[006223] = ( "INNAME")
		self.special[006222] = ( "WAITZONE")
		self.special[006224] = ( "MOVE")
		self.special[006225] = ( "INTERPRETE")

		self.special[006334] = ( "CDELAY")
		self.special[006335] = ( "WAITSE")
		self.special[006336] = ( "WAITCH")
		self.special[006337] = ( "CWANSW")
		self.special[006340] = ( "CTEST")
		self.special[006341] = ( "CPRINT")
		self.special[006343] = ( "CTOUT")
		self.special[006343] = ( "SIGNAL")
		self.special[006344] = ( "SIGCH")
		self.special[006345] = ( "CPASS")

		self.special[006346] = ( "CREATEENTRY")
		self.special[006347] = ( "LOOKUPENTRY")
		self.special[006350] = ( "CHANGEENTRY")
		self.special[006351] = ( "REMOVEENTRY")
		self.special[006352] = ( "INITCATALOG")
		self.special[006353] = ( "SETENTRY")
	
		self.special[006354] = (
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
		self.special[006355] = (
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
		self.special[006356] = (
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
		self.special[006357] = (
			"GETADR",
			(
				"     Call    return",
				"AC0  point   unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    address",
			)
		)
		self.special[006360] = (
			"GETPOINT",
			(
				"     Call    return",
				"AC0  address unchg",
				"AC1  -       unchg",
				"AC2  -       unchg",
				"AC3  link    point",
			)
		)

		self.special[006364] = ( "CSENDM")
		self.special[006365] = ( "SIGGEN")
		self.special[006366] = ( "WAITGE")
		self.special[006367] = ( "CTOP")

		self.special[006177] = ( "DIVIDE")

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

