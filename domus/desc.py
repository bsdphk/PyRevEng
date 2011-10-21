#!/usr/local/bin/python
#

import domus.const as const

#----------------------------------------------------------------------

def do_desc(p, a, l, n, desc):

	if not 'domus_desc' in p.a:
		p.a['domus_desc'] = dict()

	id = (a, l, n, desc)
	if a in p.a['domus_desc']:
		b = p.a['domus_desc'][a]
		if b == id:
			return False

		print("Redo diff desc @ " + p.m.afmt(a), b, id)
		return False

	p.a['domus_desc'][a] = id

	dtype = n + "Descriptor"

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
			x = const.dot_txt(p, a+i, a + i + j[0])
		else:
			x = const.word(p, a + i)
		x.cmt.append("+%d " % i + j[1])
		i += j[0]
		if i >= l:
			break
	while i < l:
		x = const.word(p, a + i)
		x.cmt.append("+%d" % i)
		i += 1
	return True

#----------------------------------------------------------------------

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

def pagedesc(p, adr, priv = None):
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
		priv(w)

#----------------------------------------------------------------------

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

def msgdesc(p, adr, priv = None):
	if adr == 0 or adr == None:
		return
	if do_desc(p, adr, 10, "Message", MsgDesc):
		try:
			x = p.m.rd(adr + 2)
		except:
			return
		if x != 0:
			p.todo(p.m.rd(adr + 2), msgdesc)

#----------------------------------------------------------------------

ProgDesc = (
	( 1, "spec"),
	( 1, "start"),
	( 1, "chain"),
	( 1, "size"),
	( 3, "name"),
)

def progdesc(p, adr, priv = None):
	# 1B0 = has procdesc
	# 1B1 = reentrant
	# 1B5 = params
	# 1B6 = paged
	# 1B7 = reserve
	# 1B15 = ??
	p.a['progdesc'] = adr
	do_desc(p, adr, 0, "Program", ProgDesc)

#----------------------------------------------------------------------

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

def procdesc(p, adr, priv = None):
	print("ProcDesc %x" % adr)
	p.a['procdesc'] = adr
	do_desc(p, adr, p.m.rd(adr + 3), "Process", ProcDesc)

	msgdesc(p, p.m.rd(adr + 9))

	progdesc(p, p.m.rd(adr + 10))

	if priv != None:
		# Try the PSW
		p.a['psw'] = p.m.rd(adr + 19) >> 1
		priv(p.a['psw'])

	# Try the CLEAR_INTERRUPT
	try:
		cli = p.m.rd(adr + 26)
		print("CLI " + p.m.afmt(cli))
		if cli != 0 and priv != None:
			priv(cli)
	except:
		pass

#----------------------------------------------------------------------

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

def zonedesc(p, adr, priv = None):
	do_desc(p, adr, 0, "Zone", ZoneDesc)
	x = p.m.rd(adr + 17)
	if x != 0:
		sharedesc(p, x)

#----------------------------------------------------------------------

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

def sharedesc(p, adr, priv = None):
	do_desc(p, adr, 8, "Share", ShareDesc)
