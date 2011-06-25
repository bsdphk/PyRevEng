#!/usr/local/bin/python3.2
#
# A list-based language to model instructions.
#
# Values are a tuple of (width, value) where value can be None if
# it is unknown, and False if it is unused.
#
# Syntax:
#	( Verb, arg, ...)
#	"#0b..."	binary constant, number of bits given sets width
#	"#0x..."	hex constant, number of nybbles given sets width
#	"/..."		register

class ModelError(Exception):
        def __init__(self, reason):
                self.reason = reason
                self.value = str(self.reason)
        def __str__(self):
                return repr(self.value)


class model(object):
	def __init__(self):
		self.verbs = {
		"SEQ":	self.verb_seq,
		">>":	self.verb_right_shift,
		"=":	self.verb_assign,
		"INC":	self.verb_increment,
		"DEC":	self.verb_decrement,
		}

	def setreg(self, p, state, reg, val):
		if not reg in state:
			raise ModelError("Set: register %s not in state" % reg)
		if state[reg][0] != val[0]:
			raise ModelError("Setting wrong width %d should be %d"
			    % (val[0], state[reg][0]))
		state[reg] = val

	def getreg(self, p, state, reg):
		if not reg in state:
			raise ModelError("Get: register %s not in state" % reg)
		return state[reg]

	def getint(self, p, state, val):
		w = 0
		v = 0
		if val[:3] == "#0b":
			for i in val[3:]:
				v <<= 1
				w += 1
				if i >= '0' and i <= '1':
					v |= int(i)
				else:
					raise ModelError(
					    "Int: Illegal binary" % val)
		elif val[:3] == "#0x":
			for i in val[3:]:
				v <<= 4
				w += 4
				try:
					v |= int(i, 16)
				except:
					raise ModelError(
					    "Int: Illegal octal" % val)
			pass
		else:
			raise ModelError("Int: Illegal integer" % val)
		return (w,v)

	def eval(self, p, state, expr):
		print("Eval:", expr)
		print("  State:", state)

		if type(expr) == str and expr[0] == "/":
			retval = self.getreg(p, state, expr);
		elif type(expr) == str and expr[0] == "#":
			retval = self.getint(p, state, expr);
		elif type(expr) == tuple and expr[0] in self.verbs:
			retval = self.verbs[expr[0]](p, state, expr)
		else:
			raise ModelError("Unknown expression" + str(expr))

		print("  Return:", retval)
		return retval

	def verb_seq(self, p, state, expr):
		for i in expr[1:]:
			self.eval(p, state, i)

	def verb_right_shift(self, p, state, expr):
		if len(expr) <= 1 or len(expr) > 3:
			raise ModelError("Syntax: (<< VAL BITS):" + str(expr))
		v1 = self.eval(p, state, expr[1])
		if v1[1] == None:
			return v1
		if len(expr) > 2:
			v2 = self.eval(p, state, expr[2])
		else:
			v2 = (8, 1)
		if v2[1] == None:
			raise ModelError("Verb: << BITS unknown")
		return (v1[0], v1[1] >> v2[1])

	def verb_assign(self, p, state, expr):
		if len(expr) != 3:
			raise ModelError("Syntax: (= DEST VAL):" + str(expr))
		v2 = self.eval(p, state, expr[2])
		self.setreg(p, state, expr[1], v2)

	def verb_increment(self, p, state, expr):
		if len(expr) <= 1 or len(expr) > 3:
			raise ModelError("Syntax: (INC DEST INT):" + str(expr))
		if len(expr) > 2:
			v2 = self.eval(p, state, expr[2])
		else:
			v2 = (8, 1)
		v1 = self.getreg(p, state, expr[1])
		if v1[1] != None and v2[1] != None:
			vn = (v1[0], (v1[1] + v2[1]) & ((1 << v1[0]) - 1))
		else:
			vn = (v1[0], None)
		self.setreg(p, state, expr[1], vn)
		return vn

	def verb_decrement(self, p, state, expr):
		if len(expr) <= 1 or len(expr) > 3:
			raise ModelError("Syntax: (DEC DEST INT):" + str(expr))
		if len(expr) > 2:
			v2 = self.eval(p, state, expr[2])
		else:
			v2 = (8, 1)
		v1 = self.getreg(p, state, expr[1])
		if v1[1] != None and v2[1] != None:
			vn = (v1[0], (v1[1] - v2[1]) & ((1 << v1[0]) - 1))
		else:
			vn = (v1[0], None)
		self.setreg(p, state, expr[1], vn)
		return vn

if __name__ == "__main__":

	m = model()

	si = {
		"/R1": (16,0),
	}

	m.eval(None, si, "/R1")
	m.eval(None, si, ("SEQ", "#0b001", "#0x001"))
	m.eval(None, si, (">>", "#0b101", "#0x001"))
	m.eval(None, si, ("=", "/R1", "#0x0001"))
	print(si)
	m.eval(None, si, ("INC", "/R1"))
	print(si)
	m.eval(None, si, ("DEC", "/R1", "#0x3"))
	print(si)
		

#	elif model[0] == "TRIM":
#		v1 = model_eval(p, model[1], input, ind + "\t")
#		v2 = model_eval(p, model[2], input, ind + "\t")
#		assert v2[1] != None
#		if v1[1] == None:
#			return(v2[1], None)
#		return(v2[1], v1[1] & ((1 << v2[1]) - 1))
#	elif model[0] == "MEM":
#		v = model_eval(p, model[1], input, ind + "\t")
#		if v[1] != None:
#			return (8, p.m.rd(v[1]))
#		return (8, None)
#	elif model[0] == "DISASS":
#		v = model_eval(p, model[1], input, ind + "\t")
#		# XXX: Set flow on ins
#		# XXX: Set model_in on next ins
#		if v[1] != None:
#			p.todo(v[1], p.cpu.disass)
#	else:
#		print(ind, "Unknown verb", model[0])
#		print(ind, "Model:", model)
#		print(ind, "Input:", input)
#		exit (0)
