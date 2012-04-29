#!/usr/local/bin/python
#
# Functions common to:
#	HP 5370B
#	HP 5359A
# May also be relevant to:
#	HP 5342A

# PyRevEng classes
import const

#----------------------------------------------------------------------
# Structure of (virtual) EPROMS
#
def one_eprom(p, disass, start, eprom_size):

	if False:
		x = p.t.add(start, start + eprom_size, "eprom")
		x.blockcmt += "\n-\nEPROM at 0x%x-0x%x\n\n" % \
		    (start, start + eprom_size - 1)

	# Calculate checksum
	j = 0^p.m.w16(start)
	for jj in range(2, eprom_size):
		j += p.m.rd(start + jj)
	j &= 0xffff
	if j == 0xffff:
		j = "OK"
	else:
		print("NB: Bad Eprom checksum @%x" % start)
		j = "BAD"

	x = const.w16(p, start)
	x.cmt.append("EPROM checksum (%s)" % j)

	x = const.byte(p, start + 2)
	x.cmt.append("EPROM identifier")

	# Jump table at front of EPROM
	for ax in range(start + 3, start + eprom_size, 3):
		if p.m.rd(ax) != 0x7e:
			break
		disass(ax)

def eprom(p, disass, start, end, sz):
	lx = list()
	for ax in range(start, end, sz):
		lx.append(ax >> 8)
		lx.append(ax & 0xff)
		one_eprom(p, disass, ax, sz)
	lx.append(end >> 8)
	lx.append(end & 0xff)

	# Find the table of eprom locations
	l = p.m.find(start, end, lx)
	print("EPROM", l)
	assert len(l) == 1
	x = p.t.add(l[0], l[0] + len(lx), "tbl")
	x.blockcmt += "-\nTable of EPROM locations"
	for ax in range(x.start, x.end, 2):
		const.w16(p, ax)
	p.setlabel(l[0], "EPROM_TBL")

#----------------------------------------------------------------------
# Write test values
#

def wr_test_val(p, start = 0x6000, end = 0x8000):
	px = ( 0x00, 0xff, 0xaa, 0x55, 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01)
	l = p.m.find(start, end, px)
	assert len(l) == 1
	ax = l[0]
	x = p.t.add(ax, ax + len(px), "tbl")
	print("WR_TEST_VAL", x)
	x.blockcmt += "-\nWrite Test Values"
	p.setlabel(ax, "WR_TEST_VAL")
	for i in range(x.start, x.end):
		const.byte(p, i)

def nmi_debugger(p, cpu):
	#######################################################################
	# NMI/GPIB debugger
	nmi = p.m.w16(0x7ffc)

	xnmi = p.t.add(nmi, 0x7ff8, "src")
	xnmi.blockcmt += """-
	NMI based GPIB debugger interface.
	See HPJ 1978-08 p23
	"""

	i = nmi
	l = list()
	while True:
		j = cpu.disass(i)
		if j.status == "prospective":
			print("Error: nmi_debugger called too early")
			return
		i = j.hi
		l.append(j)
		if j.mne == "BRA":
			break

	ll = None
	for i in l:
		if i.mne == "BSR":
			p.setlabel(i.lo, "NMI_LOOP()")
			x = i.flow_out[0][2]
			p.setlabel(x, "NMI_RX_A()")
		if i.mne == "CMPA":
			ll = i.oper[0]
		if i.mne == "BEQ":
			x = i.flow_out[1][2]
			if ll == "#0x01":
				p.setlabel(x, "NMI_CMD_01_WRITE() [X,L,D...]")
			elif ll == "#0x02":
				p.setlabel(x, "NMI_CMD_02_READ() [X,L]")
				kk = cpu.disass(x)
				p.setlabel(kk.flow_out[0][2],
				    "NMI_RX_X()")
			elif ll == "#0x03":
				p.setlabel(x, "NMI_CMD_03()")
			elif ll == "#0x04":
				p.setlabel(x, "NMI_CMD_04_TX_X()")
				kk = cpu.disass(x)
				while kk.mne != "BSR":
					kk = cpu.disass(kk.hi)
				p.setlabel(kk.flow_out[0][2],
				    "NMI_TX_A()")
			else:
				print(i, ll)
		if i.mne == "BRA":
			x = i.flow_out[0][2]
			p.setlabel(x, "NMI_CMD_05_END()")

#----------------------------------------------------------------------
#

def gpib_board(p):

	p.t.blockcmt += """-
0x0000-0x0003	GPIB BOARD (A15) {See HP5370B manual P8-30}

	0x0000:R Data In
	0x0000:W Data Out
	0x0001:R Inq In
	0x0001:W Status Out (P3-18)
		0x80 = Running NMI Debug monitor
		0x40 = Service Requested
		0x20 = Oven heater on
		0x10 = External Timebase
		0x0f = Error message if bit 7 "is used"
	0x0002:R Cmd In
	0x0002:W Control Out
		0x02 = NMI gate
		0x10 = EOI out {0x61e9}
	0x0003:R State In

"""

	p.setlabel(0x0000, "HPIB__DATA_IN__DATA_OUT")
	p.setlabel(0x0001, "HPIB__INQ_IN__STATUS_OUT")
	p.setlabel(0x0002, "HPIB__CMD_IN__CTRL_OUT")
	p.setlabel(0x0003, "HPIB__STATE_IN")

#----------------------------------------------------------------------
#

def display_board(p):

	p.t.blockcmt += """-
0x0060-0x007f	DISPLAY BOARD (A11)

	0x0060:R Buttons
		0xf0: scan lines
		0x07: sense lines
	0x0060-0x006f:W	LEDS
	0x0070-0x007f:W	7segs

"""

	p.setlabel(0x0060, "DISPLAY__KBD_IN__LED#0_OUT")
	p.setlabel(0x0070, "DISPLAY__7SEG#0_OUT")
	for i in range (1,16):
		p.setlabel(0x0070 + i, "DISPLAY__7SEG#%d_OUT" % i)
		p.setlabel(0x0060 + i, "DISPLAY__LED#%d_OUT" % i)

