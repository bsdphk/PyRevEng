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


	def dot_out(self, fo):
		dot = self.dot

		if dot == None and self.tp == "call":
			dot = "color=blue"

		if self.to == None and self.anondot != None:
			fo.write('FL_%x [%s]\n' % (id(self), self.anondot))
		elif self.to == None and self.tp == "ret":
			fo.write('FL_%x [shape=circle,label="ret"]\n' % id(self))
		elif self.to == None:
			fo.write('FL_%x [color=red]\n' % id(self))

		if self.fm == None and self.anondot != None:
			fo.write('FL_%x [%s]\n' % (id(self), self.anondot))
		elif self.fm == None:
			fo.write('FL_%x [color=red]\n' % id(self))

		if self.fm == None:
			fo.write('FL_%x' % id(self))
		else:
			fo.write('BB%x' % self.fm.lo)
		fo.write(" -> ")
		if self.to == None:
			fo.write('FL_%x' % id(self))
		else:
			fo.write('BB%x' % self.to.lo)
		if dot != None:
			fo.write(' [%s]' % dot)
		fo.write("\n")
	


class bb(object):
	# Properties:
	#	lo
	#	hi
	#	lang
	#	flow_in		list (dict ?)
	#	flow_out	list (dict ?)
	#	group		class group
	#	dot		str
	#
	def __init__(self, low):
		self.lo = low
		self.hi = low
		self.flow_out = list()
		self.flow_in = list()
		self.label = None
		self.dot = None

	def dot_out(self, fo):
		dot = self.dot
		if dot == None:
			dot = 'shape=box, label="'
			if self.label != None:
				dot += self.label + "\\n"
			dot += '%04x-%04x"\n' % (self.lo, self.hi)
		fo.write('BB%x [%s]\n' % (self.lo, dot))

class group(object):
	# Properties
	#	bbs		list(class bb)
	#	dot		str
	#
	def __init__(self):
		pass

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

	def dump_dot(self, filename = "/tmp/_.dot"):
		fo = open(filename, "w")
		fo.write("digraph {\n")
		for i in self.bbs:
			b = self.bbs[i]
			b.dot_out(fo)
			for j in b.flow_out:
				j.dot_out(fo)
			for j in b.flow_in:
				if j.fm == None:
					j.dot_out(fo)
		fo.write("}\n")
		fo.close()
	
