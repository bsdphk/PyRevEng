#!/usr/local/bin/python
#

from __future__ import print_function

import cpu_nova
import cpu_domus_int
import tree
import mem


class word(tree.tree):
	def __init__(self, p, adr, fmt = "%d"):
		tree.tree.__init__(self, adr, adr + 1, "word")
		p.t.add(adr, adr + 1, "word", True, self)
		self.fmt = fmt
		self.render = self.rfunc

	def rfunc(self, p, t):
		try:
			x = p.m.rd(t.start)
		except:
			return ()
		q = p.m.rdqual(t.start)
		if q == 3:
			return ((".word\t" + p.m.afmt(x/2) + "*2"),)
		elif q == 2:
			return ((".word\t" + p.m.afmt(x)),)
		else:
			return ((".word\t" + self.fmt) % x, )

class dot_txt(tree.tree):
	def __init__(self, p, start, end):
		if end == None:
			end = start
			while True:
				a = p.m.rd(end)
				if a & 0xff == 0:
					break
				if a >> 8 == 0:
					break
				end += 1
		tree.tree.__init__(self, start, end, "dot_txt")
		p.t.add(start, end, "dot_txt", True, self)
		self.render = self.rfunc

	def rfunc(self, p, t):
		s = ".TXT\t'"
		for i in range(t.start, t.end):
			q = p.m.rdqual(i)
			if q != 1:
				raise DomusError(t.start, ".TXT is relocated")
			x = p.m.rd(i)
			y = x >> 8
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
			y = x & 0xff
			if y < 32 or y > 126:
				s += "<%d>" % y
			else:
				s += mem.ascii(y)
		s += "'"
		return (s,)


def do_desc(p, a, l, n, desc):
	dtype = n + "Descriptor"
	try:
		x = p.t.find(a, dtype)
		if x != None:
			return False
	except:
		pass

	if l == 0:
		for i in desc:
			try:
				p.m.rd(a + l)
			except:
				break
			l += i[0]
	x = p.t.add(a, a + l, dtype)
	x.blockcmt += n + " descriptor\n"
	x.fill = False
	i = 0
	for j in desc:
		if j[1] == "name":
			x = dot_txt(p, a+i, a + i + j[0])
		else:
			x = word(p, a + i)
		x.cmt.append("+%d " % i + j[1])
		i += j[0]
		if i >= l:
			break
	while i < l:
		x = word(p, a + i)
		x.cmt.append("+%d" % i)
		i += 1
	return True

PageDesc = (
	( 1, "page size"),
	( 1, "page mask"),
	( 1, "blocking factor"),
	( 1, "page table"),
	( 1, "pagemap"),
	( 1, "statproc"),
	( 1, "first frame"),
	( 1, "top of frames"),
	( 1, "victim"),
	( 1, "pages read"),
	( 1, "pages written"),
	( 1, "pages in"),
	( 1, "pages out"),
	( 1, "adr input mess"),
	( 1, "input message[0]"),
	( 1, "input message[1]"),
	( 1, "input message[2]"),
	( 1, "input message[3]"),
	( 1, "adr output mess"),
	( 1, "output message[0]"),
	( 1, "output message[1]"),
	( 1, "output message[2]"),
	( 1, "output message[3]"),
	( 1, "pager flag"),
	( 1, "working locations"),
)

MsgDesc = (
	( 1, "next"),
	( 1, "prev"),
	( 1, "chain"),
	( 1, "size"),
	( 1, "sende"),
	( 1, "recei"),
	( 1, "mess0"),
	( 1, "mess1"),
	( 1, "mess2"),
	( 1, "mess3"),
)

ProgDesc = (
	( 1, "spec"),
	( 1, "start"),
	( 1, "chain"),
	( 1, "size"),
	( 3, "name"),
)

ProcDesc = (
	( 1, "next"),
	( 1, "prev"),
	( 1, "chain"),
	( 1, "size"),
	( 3, "name"),
	( 1, "first_event"),
	( 1, "last_event"),
	( 1, "buffer"),
	( 1, "program"),
	( 1, "state"),
	( 1, "timer_count"),
	( 1, "priority"),
	( 1, "break_address"),
	( 1, "ac0"),
	( 1, "ac1"),
	( 1, "ac2"),
	( 1, "ac3"),
	( 1, "psw"),
	( 1, "save"),
	( 1, "buf"),
	( 1, "address"),
	( 1, "count"),
	( 1, "reserver"),
	( 1, "conversion_table"),
	( 1, "clear_interrupt"),
)

ZoneDesc = (
	( 3, "name"),
	( 1, "size"),
	( 1, "zmode"),
	( 1, "zkind"),
	( 1, "zmask"),
	( 1, "zgive"),
	( 1, "zfile"),
	( 1, "zbloc"),
	( 1, "zconv"),
	( 1, "zbuff"),
	( 1, "zsize"),
	( 1, "zform"),
	( 1, "zleng"),
	( 1, "zfirs"),
	( 1, "ztop"),
	( 1, "zused"),
	( 1, "zshar"),
	( 1, "zrem"),
	( 1, "z0"),
	( 1, "z1"),
	( 1, "z2"),
	( 1, "z3"),
	( 1, "z4"),
	( 1, "z5"),
	( 1, "z"),
)

ShareDesc = (
	( 1, "soper" ),
	( 1, "scount" ),
	( 1, "saddr", ),
	( 1, "sspec", ),
	( 1, "snext", ),
	( 1, "sstat", ),
	( 1, "sfirs", ),
	( 1, "ssize", ),
)

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
		self.special[0o006010] = (
			 "SEARCHITEM",
			(
				"     Call    Return",
				"AC0  -       unchanged",
				"AC1  head    head",
				"AC2  name    item",
				"AC3  link    cur",
			)
		)
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
		self.special[0o006204] = (
			"TRANSFER",
			(
				"     Call    Return",
				"AC0  oper    destroyed",
				"AC1  len     destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006205] = (
			"INBLOCK",
			(
				"     Call    Return",
				"AC0  -       destroyed",
				"AC1  -       destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006206] = (
			"OUTBLOCK",
			(
				"     Call    Return",
				"AC0  -       destroyed",
				"AC1  -       destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006207] = (
			"INCHAR",
			(
				"     Call    Return",
				"AC0  -       destroyed",
				"AC1  -       char",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006210] = ( "FREESHARE",)
		self.special[0o006211] = (
			"OUTSPACE",
			(
				"     Call    Return",
				"AC0  -       unchanged",
				"AC1  -       destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006212] = (
			"OUTCHAR",
			(
				"     Call    Return",
				"AC0  -       unchanged",
				"AC1  char    destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006213] = (
			"OUTNL",
			(
				"     Call    Return",
				"AC0  -       destroyed",
				"AC1  char    destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006214] = (
			"OUTEND",
			(
				"     Call    Return",
				"AC0  -       destroyed",
				"AC1  char    destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006215] = (
			"OUTTEXT",
			(
				"     Call    Return",
				"AC0  byteadr destroyed",
				"AC1  -       destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006216] = (
			"OUTOCTAL",
			(
				"     Call    Return",
				"AC0  value   destroyed",
				"AC1  -       destroyed",
				"AC2  zone    zone",
				"AC3  link    destroyed",
			)
		)
		self.special[0o006217] = ( "SETPOSITION",)
		self.special[0o006220] = ( "CLOSE",)
		self.special[0o006221] = ( "OPEN",)
		self.special[0o006223] = ( "INNAME",)
		self.special[0o006222] = ( "WAITZONE",)
		self.special[0o006224] = ( "MOVE",)
		self.special[0o006225] = ( "INTERPRETE",)
		self.special[0o002235] = ( "NEXT_INTER",)
		self.special[0o006236] = ( "TAKEA",)
		self.special[0o006237] = ( "TAKEV",)

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
		if p.t.find(adr, "ins") != None:
			return
		assert type(adr) == int
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
		if iw == 0o006225:
			x = p.t.add(adr, adr + 1, "ins")
			x.a['mne'] = "INTERPRETE"
			x.render = self.render
			x.a['flow'] = (("cond", "F", None),)
			p.ins(x, self.disass)
			p.todo(adr + 1, cpu_domus_int.disass)
			return
		
		elif iw not in self.special:
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

	def zonedesc(self, p, adr, priv = None):
		do_desc(p, adr, 0, "Zone", ZoneDesc)
		x = p.m.rd(adr + 17)
		if x != 0:
			p.todo(x, self.sharedesc)

	def sharedesc(self, p, adr, priv = None):
		do_desc(p, adr, 8, "Share", ShareDesc)

	def progdesc(self, p, adr, priv = None):
		# 1B0 = has procdesc
		# 1B1 = reentrant
		# 1B5 = params
		# 1B6 = paged
		# 1B7 = reserve
		# 1B15 = ??
		p.a['progdesc'] = adr
		do_desc(p, adr, 0, "Program", ProgDesc)

	def procdesc(self, p, adr, priv = None):
		p.a['procdesc'] = adr
		do_desc(p, adr, p.m.rd(adr + 3), "Process", ProcDesc)

		p.cpu.msgdesc(p, p.m.rd(adr + 9))

		p.cpu.progdesc(p, p.m.rd(adr + 10))

		# Try the PSW
		p.todo(p.m.rd(adr + 19)>>1, p.cpu.disass)

		# Try the CLEAR_INTERRUPT
		try:
			cli = p.m.rd(adr + 26)
			print("CLI " + p.m.afmt(cli))
			if cli != 0:
				p.todo(cli, p.cpu.disass)
		except:
			pass

	def msgdesc(self, p, adr, priv = None):
		if adr == 0:
			return
		if do_desc(p, adr, 10, "Message", MsgDesc):
			try:
				x = p.m.rd(adr + 2)
			except:
				return
			if x != 0:
				p.todo(p.m.rd(adr + 2), self.msgdesc)

	def pagedesc(self, p, adr, priv = None):
		p.a['pagedesc'] = adr
		do_desc(p, adr, 0, "Paging", PageDesc)

		w = p.m.rd(adr + 3)
		i = p.m.rd(w)
		do_desc(p, w, i + 1, "Page_Table", (
			( 1, 		"n_pages" ),
			( i,		"pageentries"),
		))

		w = p.m.rd(adr + 4)
		i = p.m.rd(w)
		do_desc(p, w, i + 1, "Page_Map", (
			( 1,		"n_pages" ),
			( i,		"pageentries"),
		))

		w = p.m.rd(adr + 5)
		if w != 0:
			p.setlabel(w, "Paging_Statproc")
			p.todo(w, p.cpu.disass)
