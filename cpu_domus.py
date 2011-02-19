#!/usr/local/bin/python
#

from __future__ import print_function

import cpu_nova

class domus(cpu_nova.nova):
	def __init__(self):
		cpu_nova.nova.__init__(self)
		self.special = dict()
		self.special[006003] = ( "WAITINTERRUPT", 2)
		self.special[006004] = ( "SENDMESSAGE", 1)
		self.special[006005] = ( "WAITANSWER", 1)
		self.special[006006] = ( "WAITEEVENT", 2)
		self.special[006007] = ( "SENDANSWER", 1)
		self.special[006010] = ( "SEARCHITEM", 1)
		self.special[006011] = ( "CLEANPROCESS", 1)
		self.special[006012] = ( "BREAKPROCESS", 1)
		self.special[006013] = ( "STOPPROCESS", 1)
		self.special[006014] = ( "STARTPROCESS", 1)
		self.special[006015] = ( "RECHAIN", 1)
		self.special[006164] = ( "NEXTOPERATION", 3)
		self.special[006165] = ( "RETURANSWER", 1)
		self.special[006167] = ( "WAITOPERATION", 6)
		self.special[006170] = ( "SETINTERRUPT", 1)
		self.special[006171] = ( "SETRESERVATION", 1)
		self.special[006172] = ( "SETCONVERSION", 1)
		self.special[006173] = ( "CONBYTE", 1)
		self.special[006174] = ( "GETBYTE", 1)
		self.special[006175] = ( "PUTBYTE", 1)
		self.special[006176] = ( "MULTIPLY", 1)

		self.special[006232] = ( "BINDEC", 1)
		self.special[006233] = ( "DECBIN", 1)
		self.special[006200] = ( "GETREC", 1)
		self.special[006201] = ( "PUTREC", 1)
		self.special[006202] = ( "WAITTRANSFER", 1)
		self.special[006204] = ( "TRANSFER", 1)
		self.special[006205] = ( "INBLOCK", 1)
		self.special[006206] = ( "OUTBLOCK", 1)
		self.special[006207] = ( "INCHAR", 1)
		self.special[006210] = ( "FREESHARE", 1)
		self.special[006211] = ( "OUTSPACE", 1)
		self.special[006212] = ( "OUTCHAR", 1)
		self.special[006213] = ( "OUTNL", 1)
		self.special[006214] = ( "OUTEND", 1)
		self.special[006215] = ( "OUTTEXT", 1)
		self.special[006216] = ( "OUTOCTAL", 1)
		self.special[006217] = ( "SETPOSITION", 1)
		self.special[006220] = ( "CLOSE", 1)
		self.special[006221] = ( "OPEN", 1)
		self.special[006223] = ( "INNAME", 1)
		self.special[006222] = ( "WAITZONE", 1)
		self.special[006224] = ( "MOVE", 1)
		self.special[006225] = ( "INTERPRETE", 1)

		self.special[006334] = ( "CDELAY", 1)
		self.special[006335] = ( "WAITSE", 1)
		self.special[006336] = ( "WAITCH", 1)
		self.special[006337] = ( "CWANSW", 1)
		self.special[006340] = ( "CTEST", 1)
		self.special[006341] = ( "CPRINT", 1)
		self.special[006343] = ( "CTOUT", 1)
		self.special[006343] = ( "SIGNAL", 1)
		self.special[006344] = ( "SIGCH", 1)
		self.special[006345] = ( "CPASS", 1)

		self.special[006346] = ( "CREATEENTRY", 1)
		self.special[006347] = ( "LOOKUPENTRY", 1)
		self.special[006350] = ( "CHANGEENTRY", 1)
		self.special[006351] = ( "REMOVEENTRY", 1)
		self.special[006352] = ( "INITCATALOG", 1)
		self.special[006353] = ( "SETENTRY", 1)
	
		self.special[006354] = ( "COMON", 1)
		self.special[006355] = ( "CALL", -1)
		self.special[006356] = ( "GOTO", -1)
		self.special[006357] = ( "GETADR", 1)
		self.special[006360] = ( "GETPOINT", 1)

		self.special[006364] = ( "CSENDM", 1)
		self.special[006365] = ( "SIGGEN", 1)
		self.special[006366] = ( "WAITGE", 1)
		self.special[006367] = ( "CTOP", 1)

		self.special[006177] = ( "DIVIDE", 1)
		self.special[060177] = ( "INTEN", 1)
		self.special[060277] = ( "INTDS", 1)
		self.special[062677] = ( "IORST", 1)

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
		if ss[1] == -1:
			# Paging functions
			if 'page_base' in p.t.a:
				pb = p.t.a['page_base']
				nw = p.m.rd(adr + 1)
				da = (nw & 0x7fff) + pb
				p.todo(da, self.disass)
				x = p.t.add(adr + 1, adr + 2, "pgref")
				x.a['cmt'] = "pageref -> 0x%04x" % da
			if ss[0] == "CALL":
				p.todo(adr + 2, self.disass)
			
		if ss[1] > 1:
			x.a['cond'] = list()
		for j in range(1, ss[1] + 1):
			if ss[1] > 1:
				x.a['cond'].append(("XXX", adr + j))
			p.todo(adr + j, self.disass)
		p.ins(x, self.disass)

