#!/usr/local/bin/python
#

from __future__ import print_function

doc = dict()

#######################################################################
# RCSL 43-GL-9546 p34/24

doc["WAITINTERRUPT"] = (
	(
		"     Call    Return",
		"AC0  -       unchg",
		"AC1  device  device",
		"AC2  delay   cur",
		"AC3  link    cur",
	), (
		"TIMEOUT",
		"IRQ"
	)
)

#######################################################################
# RCSL 43-GL-9546 p36/26

doc["SENDMESSAGE"] = (
	(
		"     Call    Return Error",
		"AC0  -       unchg  unchg",
		"AC1  address adress adress",
		"AC2  nameadr buf    error#",
		"AC3  link    cur    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p40/30

doc["WAITANSWER"] = (
	(
		"     Call    Return",
		"AC0  -       first",
		"AC1  -       second",
		"AC2  buf     buf",
		"AC3  link    cur",
	),
)

#######################################################################
# RCSL 43-GL-9546 p42/32

doc["WAITEEVENT"] = (
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

#######################################################################
# RCSL 43-GL-9546 p44/34

doc["WAIT"] = (
	(
		"     Call    Return   Error",
		"             ans/msg  t'out/irq",
		"AC0  delay   first    unchg",
		"AC1  device  second   device",
		"AC2  buf     nextbuf  cur",
		"AC3  link    cur      cur"
	), (
		"TIMEOUT",
		"IRQ",
		"ANSWER",
		"MESSAGE"
	)
)

#######################################################################
# RCSL 43-GL-9546 p45/35

doc["SENDANSWER"] = (
	(
		"     Call    Return",
		"AC0  first   first",
		"AC1  second  second",
		"AC2  buf     buf",
		"AC3  link    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p47/37

doc["SEARCHITEM"] = (
	(
		"     Call    Return  NotFnd",
		"AC0  -       unchg   unchg",
		"AC1  head    head    head",
		"AC2  name    item    0",
		"AC3  link    cur     cur",
	),
)

#######################################################################
# RCSL 43-GL-9546 p50/40

doc["BREAKPROCESS"] = (
	(
		"     Call    Return",
		"AC0  errno   errno",
		"AC1  -       unchg ",
		"AC2  proc    proc",
		"AC3  link    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p52/42

doc["CLEANPROCESS"] = (
	(
		"     Call    Return",
		"AC0  -       unchg",
		"AC1  -       unchg ",
		"AC2  proc    proc",
		"AC3  link    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p53/43

doc["STOPPROCESS"] = (
	(
		"     Call    Return",
		"AC0  -       unchg",
		"AC1  -       unchg ",
		"AC2  proc    proc",
		"AC3  link    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p54/44

doc["STARTPROCESS"] = (
	(
		"     Call    Return",
		"AC0  -       unchg",
		"AC1  -       unchg ",
		"AC2  proc    proc",
		"AC3  link    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p54/44

doc["RECHAIN"] = (
	(
		"     Call    Return Error",
		"AC0  old     old    old",
		"AC1  new     new    new",
		"AC2  elem    elem   -3",
		"AC3  link    cur    cur"
	),
)

#######################################################################
# RCSL 43-GL-9546 p77/67

doc["NEXTOPERATION"] = (
	(
		"     Call    Return",
		"AC0  -       mode",
		"AC1  -       count",
		"AC2  cur     cur",
		"AC3  -       buf"
	), (	
		"CONTROL",
		"INPUT",
		"OUTPUT"
	)
)

#######################################################################
# RCSL 43-GL-9546 p81/71

doc["WAITOPERATION"] = (
	(
		"     Call  Tmr/Irq Answ  Msg",
		"AC0  timer unchg   -	  mode",
		"AC1  devno unchg   -	  count",
		"AC2  cur   -	    -	  cur",
		"AC3  -     cur     cur   buf",
	), (
		"TIMER",
		"IRQ",
		"ANSWER",
		"CONTROL",
		"INPUT",
		"OUTPUT"
	)
)

#######################################################################
# RCSL 43-GL-9546 p83/73

doc["RETURNANSWER"] = (
	(
		"     Call    Return",
		"AC0  status  status",
		"AC1  mess2   -",
		"AC2  cur     cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p84/74

doc["SETRESERVATION"] = (
	(
		"     Call    Return",
		"AC0  oper    oper/2",
		"AC1  -       -",
		"AC2  cur     cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p85/75

doc["SETCONVERSIOn"] = (
	(
		"     Call    Return",
		"AC0  oper    oper/2",
		"AC1  -       -",
		"AC2  cur     cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p85/75

doc["CONBYTE"] = (
	(
		"     Call    Return",
		"AC0  byte    newbyte",
		"AC1  -       -",
		"AC2  cur     cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p86/76

doc["GETBYTE"] = (
	(
		"     Call    Return",
		"AC0  -       byte",
		"AC1  byteadr byteadr",
		"AC2  -       cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p86/76

doc["PUTBYTE"] = (
	(
		"     Call    Return",
		"AC0  byte    -",
		"AC1  byteadr byteadr",
		"AC2  -       cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p88/78

doc["MULTIPLY"] = (
	(
		"     Call    Return",
		"AC0  op1     res.H",
		"AC1  op2     res.L",
		"AC2  -       cur",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p89/79

doc["DIVIDE"] = (
	(
		"     Call    Return",
		"AC0  dividen quotient",
		"AC1  divisor divisor",
		"AC2  -       cur",
		"AC3  -       reaminder"
	),
)

#######################################################################
# RCSL 43-GL-9546 p89/79

doc["SETINTERRUPT"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  devno   devno",
		"AC2  -       unchg",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p119/109

doc["OPEN"] = (
	(
		"     Call    Return",
		"AC0  oper    -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p120/110

doc["SETPOSITION"] = (
	(
		"     Call    Return",
		"AC0  block   -",
		"AC1  file    -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p121/111

doc["WAITZONE"] = (
	(
		"     Call    Return",
		"AC0  -       unchg",
		"AC1  -       unchg",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p121/111

doc["CLOSE"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  release -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p124/114

doc["TRANSFER"] = (
	(
		"     Call    Return",
		"AC0  oper    -",
		"AC1  len     -",
		"AC2  zone    zone",
		"AC3  -       -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p125/115

doc["WAITTRANSFER"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p126/116

doc["INBLOCK"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p128/118

doc["OUTBLOCK"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  -       -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p139/129

doc["GETREC"] = (
	(
		"     Call    Return",
		"AC0  bytes   bytes",
		"AC1  -       adr",
		"AC2  zone    zone",
		"AC3  link    -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p148/130

doc["PUTREC"] = (
	(
		"     Call    Return",
		"AC0  bytes   bytes",
		"AC1  -       adr",
		"AC2  zone    zone",
		"AC3  link    -"
	),
)

#######################################################################
# RCSL 43-GL-9546 p156/146

doc["MOVE"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  param   param",
		"AC3  link    -",
		"param: {#bytes, toadr, fmadr, tmp}"
	),
)

#######################################################################
# RCSL 43-GL-9546 p159/149

doc["INCHAR"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       char",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p160/150

doc["OUTCHAR"] = (
	(
		"     Call    Return",
		"AC0  -       unchanged",
		"AC1  char    -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p160/150

doc["OUTSPACE"] = (
	(
		"     Call    Return",
		"AC0  -       unchanged",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p161/151

doc["OUTEND"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  char    -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p161/151

doc["OUTNL"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p162/152

doc["OUTTEXT"] = (
	(
		"     Call    Return",
		"AC0  b'addr  -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p162/152

doc["OUTOCTAL"] = (
	(
		"     Call    Return",
		"AC0  value   -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p163/153

doc["INNAME"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  w'addr  -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p163/153

doc["DECBIN"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  b'addr  value",
		"AC2  cur     cur",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p164/154

doc["BINDEC"] = (
	(
		"     Call    Return",
		"AC0  value   -",
		"AC1  b'addr  -",
		"AC2  cur     cur",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p175/165

doc["CREATEENTRY"] = (
	(
		"     Call    Return",
		"AC0  attrib  -",
		"AC1  size    -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p175/165

doc["REMOVEENTRY"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p178/168

doc["LOOKUPENTRY"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  ptr     -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p180/170

doc["CHANGEENTRY"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  ptr     -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p180/170

doc["SETENTRY"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  ptr     -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p184/174

doc["INITCATALOG"] = (
	(
		"     Call    Return",
		"AC0  -       -",
		"AC1  unit    -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p185/175

doc["NEWCAT"] = (
	(
		"     Call    Return",
		"AC0  key     -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
# RCSL 43-GL-9546 p186/176

doc["FREECAT"] = (
	(
		"     Call    Return",
		"AC0  key     -",
		"AC1  -       -",
		"AC2  zone    zone",
		"AC3  link    -",
	),
)

#######################################################################
if False:

	self.special[0o006210] = ( "FREESHARE",)
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
