#!/usr/local/bin/python
#
# This is a demo-task which disassembles the CBM9000 boot EPROM
#

#######################################################################
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#######################################################################
# Set up a search path to two levels below

import os
sys.path.insert(0, os.path.abspath(os.path.join(".", "..", "..")))

#######################################################################
# Stuff we need...
import mem
import const
import pyreveng
import render
import topology
import cpus.mcs6500


#######################################################################
# Set up the memory image
m0 = mem.byte_mem(0, 0x010000, 0, True, "little-endian")

m0.fromfile("EPROM_Z8000_Fl.Cont._S41_6-20-85.bin", 0xe000, 1)
m0.bcols=8

#######################################################################
# Create a pyreveng instance
p = pyreveng.pyreveng(m0)

#######################################################################

p.t.blockcmt += """-
The Z8000_Schematics.pdf file reveals a number of interesting facts about
what, how and why for this chip.

p13,p35:
Pin 40 on the 6508 is not phase-2 clock, as the datasheet I have indicates,
but a "Set Overflow" pin.  The code contains a number of "BVC ."
instructions which under normal circumstances would either do nothing or
stall the CPU in a loop from which only an interrupt or reset could
dislodge it.

p34:
Memory map:
	0000		6508 I/O port data direction register

	0001		6508 I/O port
					(p13: only b7 used, to send INTEN)

	0002-003f	6508 RAM

	4000		W0MLSSSS	Drive 0 control lines
			W		Write protect, 1=protected
			 0		Track 0 detect, 1=on track 0
			  M		Motor On, 1=motor on
			   L		LED, 1=LED on
			    SSSS	Stepper control

	4001		As 4000, for drive 1

	4002		SMWEHPGG	Control lines
			S		Rd: Sync detect, 1=detected
			S		Wr: Sync generate, 1=generate
			 M		MFM mode, 0=GCR
			  W		Write gate, 1=on
			   E		Erase gate, 1=on
			    H		Head select, 0=lower
			     P		PCSS/PCSD enable, 0=drive 0
			      GG	GCR density region, 00=GCR 16 (2.66us)

	4003		8716 PCSS register select
			(from p26:)
			0xfb LD2 (b7=1: rd, b7=0: wr)
			0xfd LD1
			0xfe LD0
			0xf7 FIFO_MOVE
			0xef Rd_Status
				0x80 DMADONE
				0x40 BYTERDY
				0x20 ERROR
				0x1f RESERVED
			0x9f IRQ_HIGH
			0xbf VI_GND
			0xde (or 0xdf ?) Single-step (one word)
			0x7f Reset
			0xff Power_On

	4004		Data to and from disk

	4005		Data with PCSD select

	4006		8717 PCSD register select

	4007		TRWCSCPS	Control lines
			T		Testmode, 1=test mode
			 R		Read enable
			  W		Write current
			   C		CRC error R/O
			    S		Set CRC
			     C		Clear CRC
			      P		Precomp
			       S	Set Overflow R/O

	400c		UWNCQQQQ	Test
			U		delta
			 T		Flux change R/O
			  N		Write data R/O
			   C		Shift reg clock R/O
			    QQQQ	State R/O

	e000-f000			ROM select

p36: On-disk format:

	Track Region	Bit Time	Sect/track	Sect/reg
	1-39		2.16		16		624
	40-53		2.33		15		210
	54-64		2.50		14		154
	65-80		2.66		13		208

Derived memory map:
    HOSTADR:
	0004-0005	Host address	(0004=0x00, 0005=0x08)

	0009				Current drive 0/1

	000e		______ss	Drive 0
			      ss	Stepper-phase
	000f		______ss	Drive 1 (as 0x000e)

	0029		_dd_____	CMDx
			 dd		Drive number
			    xxxx
-
"""
#######################################################################
cpu = cpus.mcs6500.mcs6502(p)

def vector(adr, txt):
	da = p.m.l16(adr)
	x = const.w16(p, adr)
	x.lcmt(txt)
	cpu.disass(da)
	p.setlabel(da, txt)

if True:
	vector(0xfffa, "NMI")
	vector(0xfffc, "RESET")
	vector(0xfffe, "IRQ")
	for a in range(0xfff3, 0xfff9, 3):
		cpu.disass(a)
		pass

if False:
	for a in range(0xff9a, 0xffa0, 2):
		const.w16(p, a)
		cpu.disass(p.m.l16(a))
	for a in range(0xff93, 0xff9a, 3):
		const.w16(p, a + 1)
		cpu.disass(a)
		pass

if True:
	for a in range(0xe291, 0xe29d, 2):
		da = p.m.l16(a)
		const.w16(p, a)
		cpu.disass(da)

const.byte(p, 0xe962, 6)
const.byte(p, 0xe968, 5)

if False:
	# BVCLOOPs that might continue
	cpu.disass(0xe2be)

if False:
	cpu.disass(0xe034)
	cpu.disass(0xe906)
	cpu.disass(0xe90c)
	cpu.disass(0xe90e)

	cpu.disass(0xe948)

	cpu.disass(0xe96d)
	cpu.disass(0xe972)
	cpu.disass(0xe977)
	cpu.disass(0xe97c)
	cpu.disass(0xe989)
	cpu.disass(0xe98e)
	cpu.disass(0xe993)
	# cpu.disass(0xea33)
	cpu.disass(0xeab1)
	cpu.disass(0xeafb)
	#cpu.disass(0xeb0d)
	#cpu.disass(0xeb10)
	cpu.disass(0xeb13)
	cpu.disass(0xeb40)
	cpu.disass(0xeb9f)
	cpu.disass(0xebf1)
	cpu.disass(0xebff)
if False:
	cpu.disass(0xeb86)
	cpu.disass(0xeb9f)
	cpu.disass(0xebe6)
if False:
	# Plausible
	cpu.disass(0xec16)
if False:
	# contains infinite loop ?
	cpu.disass(0xec19)

while p.run():
	pass

cpu.to_tree()

const.fill(p, mid=0xfe6d)
const.fill(p, mid=0xffc0)

#######################################################################
for a in range(0xe7bf, 0xe7d3, 4):
	const.byte(p, a, 4)

const.byte(p, 0xe675, 4)
const.byte(p, 0xe679, 4)

#######################################################################
x = const.byte(p, 0xe80a, 4)
x.blockcmt += """
Stepper phase table: 0101,0110,1010,1001
"""
#######################################################################

const.byte(p, 0xe28a, 4)
#######################################################################

x = p.t.find(0xe14d, "ins")
x.blockcmt += """-
Read cmd from host

Format floppy, probably:
	04 uu 00 00 01 00 08 04 00 00 00 00 ff 00 00 00

"""

#######################################################################

p.setlabel(0xe048, "ram_err")
p.setlabel(0xe075, "good_ram")
x = p.t.find(0xe048, "ins")
x.blockcmt += """-
RAM error, flash bit(s) (LED?) to tell the world

"""
p.setlabel(0xe13f, "MotorsOff()")
p.setlabel(0xe197, "Error(A)")
p.setlabel(0xe1e6, "goto(e291[Y])")
p.setlabel(0xe1f7, "w30=swab(w2e)")
p.setlabel(0xe200, "w2e=swab(w30)")
p.setlabel(0xe244, "DMA_Rd_Addr(HOSTADR)")
p.setlabel(0xe247, "DMA_Wr_Addr(HOSTADR)")
p.setlabel(0xe264, "A=DMA_Single(X)")
p.setlabel(0xe278, "DMA_Start()")
p.setlabel(0xe323, "WriteGateOff()")
p.setlabel(0xe62e, "WriteEraseGateOn()")
p.setlabel(0xe637, "recal-ish(X)")
p.setlabel(0xe7d3, "delay_6000()")
p.setlabel(0xe7e0, "StartMotor(X)")
p.setlabel(0xe7f9, "StepDrive(X)")
p.setlabel(0x0004, "HOSTADR")

#######################################################################
# Build code graph

if True:
	p.g = topology.topology(p)
	p.g.build_bb()
	p.g.segment()
	p.g.setlabels(p)
	p.g.dump_dot()
	p.g.xxx(p)

#######################################################################
# Render output

print("Render")
r = render.render(p)
r.add_flows()
r.render("/tmp/_.cbm900_fd.txt")
