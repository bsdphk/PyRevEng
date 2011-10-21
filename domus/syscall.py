#!/usr/local/bin/python
#

from __future__ import print_function

doc = dict()

#######################################################################
# RCSL 43-GL-9546 p34/24

doc["WAITINTERRUPT"] = (
	"     Call    Return\n"
	"AC0  -       unchg\n"
	"AC1  device  device\n"
	"AC2  delay   cur\n"
	"AC3  link    cur\n"
	, (
		"TIMEOUT",
		"IRQ"
	)
)

#######################################################################
# RCSL 43-GL-9546 p36/26

doc["SENDMESSAGE"] = (
	"     Call    Return Error\n"
	"AC0  -       unchg  unchg\n"
	"AC1  address adress adress\n"
	"AC2  nameadr buf    error#\n"
	"AC3  link    cur    cur"
)

#######################################################################
# RCSL 43-GL-9546 p40/30

doc["WAITANSWER"] = (
	"     Call    Return\n"
	"AC0  -       first\n"
	"AC1  -       second\n"
	"AC2  buf     buf\n"
	"AC3  link    cur\n"
)

#######################################################################
# RCSL 43-GL-9546 p42/32

doc["WAITEEVENT"] = (
	"     Call    Return\n"
	"AC0  -       first\n"
	"AC1  -       second\n"
	"AC2  buf     next buf\n"
	"AC3  link    cur\n"
	, (
		"ANSWER",
		"MESSAGE"
	)
)

#######################################################################
# RCSL 43-GL-9546 p44/34

doc["WAIT"] = (
	"     Call    Return   Error\n"
	"             ans/msg  t'out/irq\n"
	"AC0  delay   first    unchg\n"
	"AC1  device  second   device\n"
	"AC2  buf     nextbuf  cur\n"
	"AC3  link    cur      cur"
	, (
		"TIMEOUT",
		"IRQ",
		"ANSWER",
		"MESSAGE"
	)
)

#######################################################################
# RCSL 43-GL-9546 p45/35

doc["SENDANSWER"] = (
	"     Call    Return\n"
	"AC0  first   first\n"
	"AC1  second  second\n"
	"AC2  buf     buf\n"
	"AC3  link    cur"
)

#######################################################################
# RCSL 43-GL-9546 p47/37

doc["SEARCHITEM"] = (
	"     Call    Return  NotFnd\n"
	"AC0  -       unchg   unchg\n"
	"AC1  head    head    head\n"
	"AC2  name    item    0\n"
	"AC3  link    cur     cur\n"
)

#######################################################################
# RCSL 43-GL-9546 p50/40

doc["BREAKPROCESS"] = (
	"     Call    Return\n"
	"AC0  errno   errno\n"
	"AC1  -       unchg \n"
	"AC2  proc    proc\n"
	"AC3  link    cur"
)

#######################################################################
# RCSL 43-GL-9546 p52/42

doc["CLEANPROCESS"] = (
	"     Call    Return\n"
	"AC0  -       unchg\n"
	"AC1  -       unchg \n"
	"AC2  proc    proc\n"
	"AC3  link    cur"
)

#######################################################################
# RCSL 43-GL-9546 p53/43

doc["STOPPROCESS"] = (
	"     Call    Return\n"
	"AC0  -       unchg\n"
	"AC1  -       unchg \n"
	"AC2  proc    proc\n"
	"AC3  link    cur"
)

#######################################################################
# RCSL 43-GL-9546 p54/44

doc["STARTPROCESS"] = (
	"     Call    Return\n"
	"AC0  -       unchg\n"
	"AC1  -       unchg \n"
	"AC2  proc    proc\n"
	"AC3  link    cur"
)

#######################################################################
# RCSL 43-GL-9546 p54/44

doc["RECHAIN"] = (
	"     Call    Return Error\n"
	"AC0  old     old    old\n"
	"AC1  new     new    new\n"
	"AC2  elem    elem   -3\n"
	"AC3  link    cur    cur"
)

#######################################################################
# RCSL 43-GL-9546 p77/67

doc["NEXTOPERATION"] = (
	"     Call    Return\n"
	"AC0  -       mode\n"
	"AC1  -       count\n"
	"AC2  cur     cur\n"
	"AC3  -       buf"
	, (
		"CONTROL",
		"INPUT",
		"OUTPUT"
	)
)

#######################################################################
# RCSL 43-GL-9546 p81/71

doc["WAITOPERATION"] = (
	"     Call  Tmr/Irq Answ  Msg\n"
	"AC0  timer unchg   -	  mode\n"
	"AC1  devno unchg   -	  count\n"
	"AC2  cur   -	    -	  cur\n"
	"AC3  -     cur     cur   buf\n"
	, (
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
	"     Call    Return\n"
	"AC0  status  status\n"
	"AC1  mess2   -\n"
	"AC2  cur     cur\n"
	"AC3  -       -\n"
)

#######################################################################
# RCSL 43-GL-9546 p84/74

doc["SETRESERVATION"] = (
	"     Call    Return\n"
	"AC0  oper    oper/2\n"
	"AC1  -       -\n"
	"AC2  cur     cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p85/75

doc["SETCONVERSIOn"] = (
	"     Call    Return\n"
	"AC0  oper    oper/2\n"
	"AC1  -       -\n"
	"AC2  cur     cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p85/75

doc["CONBYTE"] = (
	"     Call    Return\n"
	"AC0  byte    newbyte\n"
	"AC1  -       -\n"
	"AC2  cur     cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p86/76

doc["GETBYTE"] = (
	"     Call    Return\n"
	"AC0  -       byte\n"
	"AC1  byteadr byteadr\n"
	"AC2  -       cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p86/76

doc["PUTBYTE"] = (
	"     Call    Return\n"
	"AC0  byte    -\n"
	"AC1  byteadr byteadr\n"
	"AC2  -       cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p88/78

doc["MULTIPLY"] = (
	"     Call    Return\n"
	"AC0  op1     res.H\n"
	"AC1  op2     res.L\n"
	"AC2  -       cur\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p89/79

doc["DIVIDE"] = (
	"     Call    Return\n"
	"AC0  dividen quotient\n"
	"AC1  divisor divisor\n"
	"AC2  -       cur\n"
	"AC3  -       reaminder"
)

#######################################################################
# RCSL 43-GL-9546 p89/79

doc["SETINTERRUPT"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  devno   devno\n"
	"AC2  -       unchg\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p119/109

doc["OPEN"] = (
	"     Call    Return\n"
	"AC0  oper    -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p120/110

doc["SETPOSITION"] = (
	"     Call    Return\n"
	"AC0  block   -\n"
	"AC1  file    -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p121/111

doc["WAITZONE"] = (
	"     Call    Return\n"
	"AC0  -       unchg\n"
	"AC1  -       unchg\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p121/111

doc["CLOSE"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  release -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p124/114

doc["TRANSFER"] = (
	"     Call    Return\n"
	"AC0  oper    -\n"
	"AC1  len     -\n"
	"AC2  zone    zone\n"
	"AC3  -       -\n"
)

#######################################################################
# RCSL 43-GL-9546 p125/115

doc["WAITTRANSFER"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p126/116

doc["INBLOCK"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p128/118

doc["OUTBLOCK"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  -       -"
)

#######################################################################
# RCSL 43-GL-9546 p139/129

doc["GETREC"] = (
	"     Call    Return\n"
	"AC0  bytes   bytes\n"
	"AC1  -       adr\n"
	"AC2  zone    zone\n"
	"AC3  link    -"
)

#######################################################################
# RCSL 43-GL-9546 p148/130

doc["PUTREC"] = (
	"     Call    Return\n"
	"AC0  bytes   bytes\n"
	"AC1  -       adr\n"
	"AC2  zone    zone\n"
	"AC3  link    -"
)

#######################################################################
# RCSL 43-GL-9546 p156/146

doc["MOVE"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  param   param\n"
	"AC3  link    -\n"
	"param: {#bytes, toadr, fmadr, tmp}"
)

#######################################################################
# RCSL 43-GL-9546 p159/149

doc["INCHAR"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       char\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p160/150

doc["OUTCHAR"] = (
	"     Call    Return\n"
	"AC0  -       unchanged\n"
	"AC1  char    -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p160/150

doc["OUTSPACE"] = (
	"     Call    Return\n"
	"AC0  -       unchanged\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p161/151

doc["OUTEND"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  char    -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p161/151

doc["OUTNL"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p162/152

doc["OUTTEXT"] = (
	"     Call    Return\n"
	"AC0  b'addr  -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p162/152

doc["OUTOCTAL"] = (
	"     Call    Return\n"
	"AC0  value   -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p163/153

doc["INNAME"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  w'addr  -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p163/153

doc["DECBIN"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  b'addr  value\n"
	"AC2  cur     cur\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p164/154

doc["BINDEC"] = (
	"     Call    Return\n"
	"AC0  value   -\n"
	"AC1  b'addr  -\n"
	"AC2  cur     cur\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p175/165

doc["CREATEENTRY"] = (
	"     Call    Return\n"
	"AC0  attrib  -\n"
	"AC1  size    -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p175/165

doc["REMOVEENTRY"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p178/168

doc["LOOKUPENTRY"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  ptr     -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p180/170

doc["CHANGEENTRY"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  ptr     -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p180/170

doc["SETENTRY"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  ptr     -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p184/174

doc["INITCATALOG"] = (
	"     Call    Return\n"
	"AC0  -       -\n"
	"AC1  unit    -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p185/175

doc["NEWCAT"] = (
	"     Call    Return\n"
	"AC0  key     -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
)

#######################################################################
# RCSL 43-GL-9546 p186/176

doc["FREECAT"] = (
	"     Call    Return\n"
	"AC0  key     -\n"
	"AC1  -       -\n"
	"AC2  zone    zone\n"
	"AC3  link    -\n"
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
		"COMON\n"
		(
			"     Call    @Dest\n"
			"AC0  -       unchg\n"
			"AC1  -       unchg\n"
			"AC2  -       unchg\n"
			"AC3  link    corout\n"
		), (	
			None,
			"RETURN"
		)

	)
	self.special[0o006355] = (
		"CALL\n"
		(	
			"     Call    @Dest\n"
			"AC0  -       unchg\n"
			"AC1  -       unchg\n"
			"AC2  -       unchg\n"
			"AC3  link    link+1\n"
		), (	
			None,
			"RETURN"
		)
	)
	self.special[0o006356] = (
		"GOTO\n"
		(	
			"     Call    @Dest\n"
			"AC0  -       unchg\n"
			"AC1  -       unchg\n"
			"AC2  -       unchg\n"
			"AC3  link    destr\n"
		), (	
			None,
		)
	)
	self.special[0o006357] = (
		"GETADR\n"
		(
			"     Call    return\n"
			"AC0  point   unchg\n"
			"AC1  -       unchg\n"
			"AC2  -       unchg\n"
			"AC3  link    address\n"
		)
	)
	self.special[0o006360] = (
		"GETPOINT\n"
		(
			"     Call    return\n"
			"AC0  address unchg\n"
			"AC1  -       unchg\n"
			"AC2  -       unchg\n"
			"AC3  link    point\n"
		)
	)
