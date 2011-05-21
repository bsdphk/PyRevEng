#!/usr/local/bin/python
#

from __future__ import print_function

import array

class DomusFileError(Exception):
	def __init__(self, reason):
		self.reason = reason
		self.value = str(self.reason)
	def __str__(self):
		return repr(self.value)


def radix40(y):
	s = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.?"
	v1 = y[0]
	v2 = y[1]
	l3 = v1 % 40
	l2 = int(v1 / 40) % 40
	l1 = int(v1 / (40*40)) % 40
	l5 = int(v2 / 32) % 40
	l4 = int(v2 / (40 * 32)) % 40
	#print(len(s), l1, l2, l3, l4, l5, s[l1], s[l2], s[l3], s[l4], s[l5])
	return ((s[l1] + s[l2] + s[l3] + s[l4] + s[l5]).strip(), v2 & 0x1f)

class file_domus(object):
	def __init__(self, filename):
		# Read the entire file
		f = open(filename, "rb")
		self.d = array.array("H", f.read())
		self.filename = filename
		f.close()
		self.index = self.build_index()

	def build_index(self):
		# Builds index of objects in file
		l=dict()
		a = 0
		a0 = a
		titl = None
		while a < len(self.d):
			rec_typ = self.d[a]
			if rec_typ > 9:
				break
			if rec_typ == 0:
				a += 1
				a0 = a
				continue
			a += 1

			rec_len = self.d[a] - 65536
			assert rec_len > -16 and rec_len < 0
			a += 1

			# XXX: Check checksum

			a += 4 - rec_len

			if rec_typ == 7:
				titl = radix40(self.d[a0 + 6:a0+9])[0]
			if rec_typ == 6:
				l[titl] = (a0, a)
				titl = None
				a0 = a
		return l

	def load(self, mem, obj=None, off = 0x1000, offhi=0x8000, silent=False):
		if obj == None:
			if len(self.index) != 1:
				raise DomusFileError(
				    "More than one object in file")
			for i in self.index:
				obj = i
		if obj not in self.index:
			raise DomusFileError(
			    "Object not found in file:" + obj)
		if not silent:
			print("LOAD ", obj)
		self.rec_end = None
		self.rec_titl = None
		self.rec_size = None
		self.load_words = 0
		self.max_nrel = 0
		self.max_zrel = 0
		a,ae = self.index[obj]
		while a < ae:
			rec_typ = self.d[a]
			rec_len = self.d[a + 1] - 65536
			s = "%d" % rec_typ
			s += " %3d" % rec_len
			rl = ""
			for i in range(2,5):
				r = "%05o" % (self.d[a + i] / 2)
				s += " " + r
				rl += r
			s += " %04x" % self.d[a + 5]
			s += " %04x" % self.d[a + 6]
			y = list()
			z = list()
			for i in range(6,6 - rec_len):
				x = self.d[a + i]
				z.append(int(rl[0]))
				if rl[0] == "0":
					s += " %04x " % x
					y.append(x)
				elif rl[0] == "1":
					s += " %04x " % x
					y.append(x)
				elif rl[0] == "2":
					s += " %04x'" % x
					y.append(x + off)
				elif rl[0] == "3":
					s += ' %04x"' % x
					y.append(x + off * 2)
				elif rl[0] == "7":
					s += " %04x*" % x
					y.append(x + offhi)
				else:
					raise DomusFileError(
					    "Wrong Reloc %s" % rl[0])
				rl = rl[1:]
			if rec_typ == 2:
				ax = y[0]
				for i in range(1, len(y)):
					if ax < offhi and ax > self.max_nrel:
						self.max_nrel = ax
					if ax >= offhi and ax > self.max_zrel:
						self.max_zrel = ax
					self.load_words += 1
					mem.setflags(ax, None,
					    mem.can_read | mem.can_write,
					    mem.invalid)
					mem.wr(ax, y[i] & 0xffff)
					mem.wrqual(ax, z[i])
					ax += 1
			elif rec_typ == 6:
				if not silent:
					print("\t.END %04x" % y[0])
				self.rec_end = y[0]
			elif rec_typ == 7:
				self.rec_titl = radix40(y)
				if not silent:
					print("\t.TITL\t%s" % self.rec_titl[0])
			elif rec_typ == 9:
				self.rec_size = y
			else:
				raise DomusFileError(
				    "Load Unknown Record %d" % rec_typ)

			if not silent:
				print(s)
			a += 6 - rec_len

if __name__ == "__main__":

	import mem

	dn="/rdonly/DDHF/oldcritter/DDHF/DDHF/RC3600/Sw/Rc3600/rc3600/__/"
	fn = dn + "__.MUM"
	fn = dn + "__.FSLIB"
	fn = dn + "__.ULIB"
	fn = dn + "__.CATLI"
	fn = dn + "__.PTP"
	fn = dn + "__.DOMAC"
	fn = dn + "__.DOMUS"

	fn = dn + "__.CATLI"

	df = file_domus(fn)
	for i in df.index:
		print(i)
	m = mem.base_mem(0, 0x10000, 16, 3, True)
	df.load(m)
	print("END", df.rec_end)
	print("TITLE", df.rec_titl)
	print("HIMEM", df.rec_size)
