#!/usr/local/bin/python
#

from __future__ import print_function

class nova(object):
	def __init__(self):
		self.dummy = True

	def adrmode(self, p, adr,iw):
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
				x.a['cond'] = (("NXT", adr + 2),)
			elif cc:
				x.a['cond'] = ((o3, adr + 2), (o3n, adr + 1,))
		elif iw & 0xe000 == 0x0000:
			s = ("JMP", "JSR", "ISZ", "DSZ")[(iw>>11)&3]
			x.a['mne'] = s
			i=self.adrmode(p, adr, iw)
			x.a['oper'] = i[1]
			if s == "JMP":
				x.a['cond'] = (("T", i[0]),)
			elif s == "JSR":
				x.a['call'] = (("T", i[0]),)
			else:
				x.a['cond'] = (("NZ", adr + 1), ("Z", adr + 2))
		elif iw & 0xe000 == 0x6000:
			s = ("NIO", "DIA", "DOA", "DIB",
			     "DOB", "DIC", "DOC", "SKP")[(iw>>8)&7]
			if s == "SKP":
				s1 = ("BN", "BZ", "DN", "DZ")[(iw>>6)&3]
				s += s1
				s2 = ("BN", "BZ", "DN", "DZ")[((iw>>6)&3) ^ 1]
				x.a['cond'] = ((s2, adr + 1), (s1, adr + 2))
			else:
				s += ("", "S", "C", "P")[(iw>>6)&3]
			x.a['mne'] = s
			if s[0] == "D":	
				o1 = "%d" % ((iw >> 11) & 3)
				o2 = "%d" % (iw & 0x3f)
				x.a['oper'] = (o1, o2)
			else:
				o1 = "%d" % (iw & 0x3f)
				x.a['oper'] = (o1,)
		else:
			s = ("", "LDA", "STA")[(iw>>13)&3]
			x.a['mne'] = s
			o1 = "%d" % ((iw>>11)&3)
			i=self.adrmode(p, adr, iw)
			x.a['oper'] = (o1,) + i[1]

		p.ins(x, self.disass)
