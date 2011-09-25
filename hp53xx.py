#!/usr/local/bin/python
#
# Functions common to:
#	HP 5370B
#	HP 5359A
# May also be relevant to:
#	HP 5342A

from __future__ import print_function

# PyRevEng classes
import const

#----------------------------------------------------------------------
# Structure of (virtual) EPROMS
#
def one_eprom(p, start, eprom_size):

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

	# Handle any 0xff fill at the end of this EPROM
	n = 0
	for a in range(start + eprom_size - 1, start, -1):
		if p.m.rd(a) != 0xff:
			break;
		n += 1
	if n > 1:
		x = p.t.add(start + eprom_size - n, start + eprom_size, "fill")
		x.render = ".FILL\t%d, 0xff" % n

	# Jump table at front of EPROM
	for ax in range(start + 3, start + eprom_size, 3):
		if p.m.rd(ax) != 0x7e:
			break
		p.todo(ax, p.cpu.disass)

def eprom(p, start, end, sz):
	lx = list()
	for ax in range(start, end, sz):
		lx.append(ax >> 8)
		lx.append(ax & 0xff)
		one_eprom(p, ax, sz)
	lx.append(end >> 8)
	lx.append(end & 0xff)

	# Find the table of eprom locations
	l = p.m.find(start, end, lx)
	print("EPROM", l)
	assert len(l) == 1
	x = p.t.add(l[0], l[0] + len(lx), "tbl")
	x.blockcmt += "\n-\nTable of EPROM locations\n\n"
	for ax in range(x.start, x.end, 2):
		const.w16(p, ax)
	p.setlabel(l[0], "EPROM_TBL")

#----------------------------------------------------------------------
# Character Generator for 7-segments
#

def sevenseg(p, y, val):
	if val & 0x01:
		y.cmt.append("  --")
	else:
		y.cmt.append("    ")

	if val & 0x20:
		s = " |"
	else:
		s = "  "
	if val & 0x02:
		y.cmt.append(s + "  |")
	else:
		y.cmt.append(s + "   ")

	if val & 0x40:
		y.cmt.append("  --")
	else:
		y.cmt.append("    ")

	if val & 0x10:
		s = " |"
	else:
		s = "  "
	if val & 0x04:
		y.cmt.append(s + "  |")
	else:
		y.cmt.append(s + "   ")

	if val & 0x08:
		s = "  -- "
	else:
		s = "     "
	if val & 0x80:
		y.cmt.append(s + ".")
	else:
		y.cmt.append(s)
	y.cmt.append(" ")


def chargen(p, start = 0x6000, end = 0x8000, chars=16):

	px = (0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07,
	     0x7f, 0x6f, 0x80, 0xff, 0x40, 0x79, 0x50, 0x00)

	l = p.m.find(start, end, px)
	assert len(l) == 1

	ax = l[0]
	x = p.t.add(ax, ax + chars, "tbl")
	print("CHARGEN", x)
	x.blockcmt += "\n-\nBCD to 7 segment table\n\n"
	p.setlabel(ax, "CHARGEN")
	for i in range(0,chars):
		y = const.byte(p, x.start + i)
		w = p.m.rd(x.start + i)
		sevenseg(p, y, w)


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
	x.blockcmt += "\n-\nWrite Test Values\n\n"
	p.setlabel(ax, "WR_TEST_VAL")
	for i in range(x.start, x.end):
		const.byte(p, i)

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

