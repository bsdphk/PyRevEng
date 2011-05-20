#!/usr/local/bin/python
#
# This is a disassembler for the Data General Nova CPU
#
# There are two extension mechanisms which do not require subclassing:
#
#	self.intercept[instuction_word] = (function_to_call, private_argument)
#		Special instructions can be handled this way
#
#	self.iodev[device_number] = "device_name"
#		Name the I/O devices
#

from __future__ import print_function

class nova(object):
	def __init__(self):
		self.dummy = True
		self.intercept = {
			0o060177: ( self.macro,	("INTEN",)),
			0o060277: ( self.macro,	("INTDS",)),
			0o060477: ( self.cpu,	("READS",)),
			0o064477: ( self.cpu,	("READS",)),
			0o070477: ( self.cpu,	("READS",)),
			0o074477: ( self.cpu,	("READS",)),
			0o061477: ( self.cpu,	("INTA",)),
			0o065477: ( self.cpu,	("INTA",)),
			0o071477: ( self.cpu,	("INTA",)),
			0o075477: ( self.cpu,	("INTA",)),
			0o062077: ( self.cpu,	("MSKO",)),
			0o066077: ( self.cpu,	("MSKO",)),
			0o072077: ( self.cpu,	("MSKO",)),
			0o076077: ( self.cpu,	("MSKO",)),
			0o062677: ( self.cpu,	("IORST",)),
			0o066677: ( self.cpu,	("IORST",)),
			0o072677: ( self.cpu,	("IORST",)),
			0o076677: ( self.cpu,	("IORST",)),
			0o063077: ( self.cpu,	("HALT",)),
			0o067077: ( self.cpu,	("HALT",)),
			0o073077: ( self.cpu,	("HALT",)),
			0o077077: ( self.cpu,	("HALT",)),
			0o063477: ( self.macro,	("SKPIRQ",)),
			0o063577: ( self.macro,	("SKPNIRQ",)),
			0o063677: ( self.macro,	("SKPPWR",)),
			0o063777: ( self.macro,	("SKPNPWR",)),
		}
		self.iodev = {
			63: "CPU",
		}

	def cpu(self, p, adr, priv):
		iw = p.m.rd(adr)
		x = p.t.add(adr, adr + 1, "ins")
		x.render = self.render
		x.a['mne'] = priv[0]
		x.a['oper'] = ("%d" % ((iw>>11)&3),)
		f = (iw>>8)&3
		if f == 1:
			x.a['oper'] += ("INTEN",)
		elif f == 2:
			x.a['oper'] += ("INTDS",)
		p.ins(x, self.disass)
		return x

	def macro(self, p, adr, priv):
		x = p.t.add(adr, adr + 1, "ins")
		x.render = self.render
		x.a['mne'] = priv[0]
		if len(priv) > 1:
			x.a['oper'] = priv[1]
		p.ins(x, self.disass)
		return x

	def adrmode(self, p, adr,iw):
		# NB: Unless memory extension involved, in mode 2 & 3, the
		# NB: topbit is zeroed, so AC2=0xff53 + displacement 0x4f does
		# NB: not yield 0x801a, but 0x001a
		d = iw & 0xff
		mode =  (iw>>8)&3
		if iw & 0x400:
			o0 = "@"
		else:
			o0 = ""
		o2 = "%d" % mode
		o4 = None
		if d < 128:
			o1 = "%d" % d
		else:
			o1 = "%d" % (d-256)
		if mode == 0:
			o1 = "%d" % d
			o4 = d
		elif mode == 1 and d < 128:
			o4 = adr + d
		elif mode == 1:
			o4 = adr + d - 256
		if o4 != None and o0 == "@":
			try:
				o4 = p.m.rd(o4)
			except:
				o4 = None
		return (o4, (o0 + o1, o2))

	def render(self, p, t, lvl):
		s = t.a['mne'] + "\t"
		if 'oper' in t.a:
			d = ""
			for i in t.a['oper']:
				s += d
				s += str(i)
				d = ','
		return (s,)

	def disass(self, p, adr, priv):
		try:
			iw = p.m.rd(adr)
		except:
			return

		if iw in self.intercept:
			m = self.intercept[iw]
			return m[0](p, adr, m[1])

		x = p.t.add(adr, adr + 1, "ins")
		x.render = self.render
		if iw & 0x8000:
			s = ("COM", "NEG", "MOV", "INC",
			     "ADC", "SUB", "ADD", "AND")[(iw>>8)&7]
			s += ("", "Z", "O", "C")[(iw>>4)&3]
			s += ("", "L", "R", "S")[(iw>>6)&3]
			if iw & 0x8:
				s += "#"
			x.a['mne'] = s
			o1 = '%d' % ((iw >> 13)&3)
			o2 = '%d' % ((iw >> 11)&3)
			cc = iw & 7
			if cc:
				o3 = ("", "SKP", "SZC", "SNC",
				      "SZR", "SNR", "SEZ", "SBN")[cc]
				o3n = ("", "SKP", "SZC", "SNC",
				      "SZR", "SNR", "SEZ", "SBN")[cc ^ 0x1]
				x.a['oper'] = (o1, o2, o3)
				x.a['oper'] = (o1, o2, o3)
			else:
				x.a['oper'] = (o1, o2)
			if cc == 1:
				x.a['flow'] = (("cond", "T", adr + 2),)
			elif cc:
				x.a['flow'] = (
				    ("cond", o3, adr + 2),
				    ("cond", o3n, adr + 1,))
		elif iw & 0xe000 == 0x0000:
			s = ("JMP", "JSR", "ISZ", "DSZ")[(iw>>11)&3]
			x.a['mne'] = s
			i=self.adrmode(p, adr, iw)
			x.a['oper'] = i[1]
			if iw == 0o002401:
				x.a['flow'] = (("cond", "T", p.m.rd(adr + 1)),)
			elif s == "JMP":
				x.a['flow'] = (("cond", "T", i[0]),)
			elif s == "JSR":
				x.a['flow'] = (("call", "T", i[0]),)
			else:
				x.a['flow'] = (
				    ("cond", "NZ", adr + 1),
				    ("cond", "Z", adr + 2))
				if i[0] != None:
					x.a['EA'] = (i[0],)
			
		elif iw & 0xe000 == 0x6000:
			s = ("NIO", "DIA", "DOA", "DIB",
			     "DOB", "DIC", "DOC", "SKP")[(iw>>8)&7]
			if s == "SKP":
				s1 = ("BN", "BZ", "DN", "DZ")[(iw>>6)&3]
				s += s1
				s2 = ("BN", "BZ", "DN", "DZ")[((iw>>6)&3) ^ 1]
				x.a['flow'] = (
				    ("cond", s2, adr + 1),
				    ("cond", s1, adr + 2))
			else:
				s += ("", "S", "C", "P")[(iw>>6)&3]
			x.a['mne'] = s
			dev = iw & 0x3f
			if dev in self.iodev:
				dev = self.iodev[dev]
			else:
				dev = "%d" % dev
			if s[0] == "D":	
				o1 = "%d" % ((iw >> 11) & 3)
				o2 = dev
				x.a['oper'] = (o1, o2)
			else:
				o1 = dev
				x.a['oper'] = (o1,)
		else:
			s = ("", "LDA", "STA")[(iw>>13)&3]
			x.a['mne'] = s
			o1 = "%d" % ((iw>>11)&3)
			i=self.adrmode(p, adr, iw)
			x.a['oper'] = (o1,) + i[1]
			if i[0] != None:
				x.a['EA'] = (i[0],)

		p.ins(x, self.disass)
