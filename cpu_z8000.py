#!/usr/local/bin/python
#
# Zilog Z800[12] CPU disassembler
#

from __future__ import print_function

class z8000(object):
	def __init__(self):
		self.dummy = True

	def render(self, p, t):
		s = t.a['mne']
		s += "\t"
		d = ""
		if 'DA' in t.a:
			da = t.a['DA']
			if da in p.label:
				return (s + p.label[da] +
				    " (" + p.m.afmt(da) + ")",)
		for i in t.a['oper']:
			s += d
			s += str(i)
			d = ','
		return (s,)

	def disass(self, p, adr, priv = None):
		if p.t.find(adr, "ins") != None:
			return
		try:
			iw = p.m.rd(adr)
			iw2 = p.m.rd(adr + 1)
		except:
			print("FETCH failed:", adr)
			return

		if iw == 0x21 and (iw2 & 0xf0) == 0x00:
			# p120/111
			x = p.t.add(adr, adr + 4, "ins")
			x.a['mne'] = "LD"
			x.a['oper'] = (
			    "R%d" % (iw2 & 0x0f),
			    "0x%04x" % p.m.b16(adr + 2)
			)
			x.render = self.render
			p.todo(adr + 4, self.disass)
		elif iw == 0x3b and (iw2 & 0x0f) == 0x07:
			# p161/152
			x = p.t.add(adr, adr + 4, "ins")
			x.a['mne'] = "SOUT"
			x.a['oper'] = (
			    "0x%04x" % p.m.b16(adr + 2),
			    "R%d" % (iw2 >> 4),
			)
			x.render = self.render
			p.todo(adr + 4, self.disass)
		elif iw == 0x7d and (iw2 & 0x0f) == 0x0a:
			# p129/120
			x = p.t.add(adr, adr + 2, "ins")
			x.a['mne'] = "LDCTL"
			x.a['oper'] = ("FCW", "R%d" % (iw2 >> 4),)
			x.render = self.render
			p.todo(adr + 2, self.disass)
		elif iw == 0x7d and (iw2 & 0x0f) == 0x0c:
			# p129/120
			x = p.t.add(adr, adr + 2, "ins")
			x.a['mne'] = "LDCTL"
			x.a['oper'] = ("PSAPOFF", "R%d" % (iw2 >> 4),)
			x.render = self.render
			p.todo(adr + 2, self.disass)
		elif iw == 0x8d and (iw2 & 0x0f) == 0x08:
			# p75/66
			x = p.t.add(adr, adr + 2, "ins")
			x.a['mne'] = "CLR"
			x.a['oper'] = ("R%d" % (iw2 >> 4),)
			x.render = self.render
			p.todo(adr + 2, self.disass)
		else:
			print("Z8k: Unknown Inst", p.m.afmt(adr),
			    p.m.dfmt(iw), p.m.dfmt(iw2))

