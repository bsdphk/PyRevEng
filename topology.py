#/usr/local/bin/python3.2
#
# Topological flow analysis



class flow(object):
	# Properties:
	#	fm		{None, str or BB}
	#	to		{None, str or BB}
	#	tp		{"goto", "call", "ret"}
	#	subtype		str
	#	condition 	{"T", "F", str}
	#	offpage		bool
	#	dot		str
	#	anondot		str
	#
	def __init__(self, fm, to, tp = "goto"):

		self.tp = tp
		self.subtype = None
		self.condition = "T"
		self.offpage = None
		self.dot = None
		self.anondot = None

		if type(fm) == str:
			self.anondot = 'shape=circle,label="%s",color=green' % fm
			self.dot = 'color=green'
			self.fm = None
		else:
			self.fm = fm
			if self.fm != None:
				self.fm.flow_out.append(self)

		if type(to) == str:
			self.anondot = 'shape=circle,label="%s",color=green' % to
			self.dot = 'color=green'
			self.to = None
		else:
			self.to = to
			if self.to != None:
				self.to.flow_in.append(self)

		assert self.fm != None or self.to != None


	def dot_fmt(self, fo, fm, to):
		dot = self.dot

		if dot == None and self.tp == "call":
			dot = "color=blue"

		if fm:
			fmn = "BB%x" % self.fm.lo
		else:
			fmn = "FLF%x" % id(self)
			if self.fm != None:
				self.fm.dot_fmt(fo, fmn)

		if to:
			ton = "BB%x" % self.to.lo
		else:
			ton = "FLT%x" % id(self)
			if self.to != None:
				self.to.dot_fmt(fo, ton)

		if self.to == None and self.anondot != None:
			fo.write(ton + ' [' + self.anondot + ']\n')
		elif self.to == None and self.tp == "ret":
			# subtype
			fo.write(ton + ' [shape=circle,label="ret"]\n')
		elif self.to == None:
			fo.write(ton + ' [color=red]\n')

		if self.fm == None and self.anondot != None:
			fo.write(fmn + ' [' + self.anondot + ']\n')
		elif self.fm == None:
			fo.write(fmn + ' [color=red]\n')

		fo.write(fmn + ' -> ' + ton)
		if dot != None:
			fo.write(' [' + dot + ']')
		fo.write("\n")

	def dot_out(self, fo, b):
		if self.offpage or self.to == None:
			self.dot_fmt(fo, True, False)
		else:
			self.dot_fmt(fo, True, True)

	def dot_in(self, fo, b):
		if self.offpage or self.fm == None:
			self.dot_fmt(fo, False, True)


class bb(object):
	# Properties:
	#	lo
	#	hi
	#	lang
	#	flow_in		list (dict ?)
	#	flow_out	list (dict ?)
	#	segment		class segment
	#	dot		str
	#
	def __init__(self, low):
		self.lo = low
		self.hi = low
		self.flow_out = list()
		self.flow_in = list()
		self.label = None
		self.segment = None
		self.dot = None

	def dot_fmt(self, fo, nm=None):
		dot = self.dot
		if nm == None:
			nmx = "BB%x" % self.lo
		else:
			nmx = nm
		if dot == None:
			if nm == None:
				dot = 'shape=box, label="'
			else:
				dot = 'shape=plaintext, label="'
			if self.label != None:
				dot += self.label + "\\n"
			dot += '%04x-%04x' % (self.lo, self.hi)
			if self.segment != None and self.segment.label != None:
				dot += '\\n{' + self.segment.label + '}'
			dot += '"'
		fo.write(nmx + ' [' + dot + ']\n')

class segment(object):
	# Properties
	#	bbs		list(class bb)
	#	label		str
	#	digraph		str
	#
	def __init__(self):
		self.bbs = list()
		self.label = None
		self.digraph = ""
		self.lo = None
		self.hi = None

	def dot_fmt(self, fo):
		fo.write('Segment [shape=parallelogram,label="%04x-%04x"]\n' % (self.lo, self.hi))
		for b in self.bbs:
			b.dot_fmt(fo)
			for j in b.flow_out:
				j.dot_out(fo, b)
			for j in b.flow_in:
				j.dot_in(fo, b)

class topology(object):
	# Properties
	#	TBD
	#
	def __init__(self, tree):
		self.src_flow_in = dict()
		self.src_flow_out = dict()
		self.tree = tree
		self.idx = dict()
		self.bbs = dict()
		self.segments = list()
		self.tree.recurse(self.collect_flows)

	def collect_flows(self, tree, priv, lvl):
		if tree.start in self.idx:
			t = self.idx[tree.start]
			assert t.start == tree.start
			if tree.end - tree.start < t.end - t.start:
				self.idx[tree.start] = tree
		else:
			self.idx[tree.start] = tree

		if not 'flow' in tree.a:
			return
		if not tree.start in self.src_flow_out:
			self.src_flow_out[tree.start] = True
		for j in tree.a['flow']:
			dst = j[2]
			if type(dst) == int:
				if not dst in self.src_flow_in:
					self.src_flow_in[dst] = tree.tag

	def build_bb(self):
		for i in self.src_flow_in.keys():
			if i not in self.idx:
				print("NOTE: %x was not in tree" % i)
				continue
			self.bbs[i] = bb(i)

		for i in self.bbs.keys():
			b = self.bbs[i]
			lo = i
			nxt = lo
			hi = self.idx[nxt].end
			while True:
				if 'flow' in self.idx[nxt].a:
					for j in self.idx[nxt].a['flow']:
						dst = j[2]
						if type(dst) != int:
							f = flow(b, None)
						elif dst not in self.bbs:
							print("NOTE: %x was not in bbs" % dst, "(%s)" % str(j))
							f = flow(b, None)
							f.anondot='shape=hexagon,label="%04x"' % dst
						else:
							f = flow(b, self.bbs[dst])
						f.condition = j[1]
						if len(j) > 3:
							f.subtype = j[3]
						if j[0] == "cond":
							f.tp = "goto"
							f.offpage = False
							pass
						elif j[0] == "call":
							f.tp = "call"
							f.offpage = True
							pass
						elif j[0] == "ret":
							f.tp = "ret"
							f.offpage = True
							pass
						else:
							print("NOTE: Unknown flow input (%s)" % str(j))
				if nxt in self.src_flow_out:
					x = False
					for i in self.idx[nxt].a['flow']:
						if i[0] == "call":
							continue
						x = True
						break
					if x:
						break
				if hi in self.src_flow_in:
					f = flow(b, self.bbs[hi])
					break
				nxt = hi
				hi = self.idx[nxt].end
			b.hi = hi

	##################################################################

	def setlabel(self, adr, lbl):
		if adr not in self.bbs:
			print("ERROR: %x is not a BB" % adr)
		if self.bbs[adr].label != None and self.bbs[adr].label != lbl:
			print("NOTE: %x changed label from" % adr, self.bbs[adr].label, "to", lbl)
		self.bbs[adr].label = lbl

	##################################################################

	def findflow(self, fm, to):
		if fm not in self.bbs:
			print("ERROR: %x is not a BB" % fm)
			return
		fm = self.bbs[fm]
		if to not in self.bbs:
			print("ERROR: %x is not a BB" % to)
			return
		to = self.bbs[to]
		for ff in fm.flow_out:
			if ff.to == to:
				return ff
		return

	##################################################################
	# Segmentation

	def __bust_seg(self, g):
		print("BUSTING %04x-%04x" % (g.lo, g.hi))
		for i in g.bbs:
			i.segment = None
		self.segments.remove(g)
		del g

	def __do_seg(self, g, bb):
		if bb.segment == g:
			return True
		if bb.segment != None:
			print("ERR: bb.seg %04x-%04x" % (bb.segment.lo, bb.segment.hi))
		assert bb.segment == None
		if g.lo == None:
			g.lo = bb.lo
			g.hi = bb.hi
			for i in self.segments:
				if i == g:
					continue
				if g.lo >= i.lo and g.lo < i.hi:
					print("BUSTING.lo %04x-%04x vs %04x-%04x" % (g.lo, g.hi, i.lo, i.hi))
					self.__bust_seg(i)
				elif g.hi > i.lo and g.hi <= i.hi:
					print("BUSTING.hi %04x-%04x vs %04x-%04x" % (g.lo, g.hi, i.lo, i.hi))
					self.__bust_seg(i)
		elif bb.lo < g.lo:
			for i in self.segments:
				if i == g:
					continue
				if i.lo >= bb.lo and i.hi <= g.lo:
					#print("COLL_LO: BB %04x-%04x G %04x-%04x vs G %04x-%04x" % (bb.lo, bb.hi, g.lo,g.hi, i.lo,i.hi))
					return False
			g.lo = bb.lo
		elif bb.hi > g.hi:
			for i in self.segments:
				if i == g:
					continue
				if i.lo >= g.hi and i.hi <= bb.lo:
					#print("COLL_HI: BB %04x-%04x G %04x-%04x vs G %04x-%04x" % (bb.lo, bb.hi, g.lo,g.hi, i.lo,i.hi))
					return False
			g.hi = bb.hi

		bb.segment = g
		g.bbs.append(bb)
		for ff in bb.flow_out:
			if ff.offpage:
				continue
			if ff.to != None:
				if not self.__do_seg(g, ff.to):
					ff.offpage = True
		for ff in bb.flow_in:
			if ff.offpage:
				continue
			if ff.fm != None:
				if not self.__do_seg(g, ff.fm):
					ff.offpage = True
		return True

	def segment(self, adr = None, label = None):
		if adr != None:
			if adr not in self.bbs:
				print("ERROR: %x is not a BB" % adr)
				return
			bb = self.bbs[adr]
			if bb.segment != None:
				print("ERROR: %x is already segmented" % adr, bb.segment.label)
				return
			assert bb.segment == None
			g = segment()
			g.label = label
			self.segments.append(g)
			self.__do_seg(g, bb)
			return g
		done = True
		while done:
			done = False
			for b in self.bbs.keys():
				if self.bbs[b].segment != None:
					continue
				g = segment()
				self.segments.append(g)
				self.__do_seg(g, self.bbs[b])
				done = True
			self.segments.sort(key=lambda x: x.lo)

	##################################################################
	# DOT graph output

	def dump_dot(self, filename = "/tmp/_.dot", digraph=""):
		fo = open(filename, "w")
		for gg in self.segments:
			fo.write("digraph {\n" + digraph + "\n" + gg.digraph + "\n")
			gg.dot_fmt(fo)
			fo.write("}\n")
		xxx = False
		for i in self.bbs:
			b = self.bbs[i]
			if b.segment != None:
				continue
			if not xxx:
				fo.write("digraph {\n")
				xxx = True
			b.dot_fmt(fo)
			for j in b.flow_out:
				j.dot_out(fo, b)
			for j in b.flow_in:
				j.dot_in(fo, b)
		if xxx:
			fo.write("}\n")
		fo.close()
