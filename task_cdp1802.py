#!/usr/local/bin/python3.2

import mem
import pyreveng

import cpu_cdp1802

m = mem.byte_mem(0,0x10000, 0, True, "big-endian")

m.bcols = 3

p = pyreveng.pyreveng(m)
p.cmt_start = 56
p.m.fromfile("cdp1802.bin", 0x0000, 1)
p.cpu = cpu_cdp1802.cdp1802()

p.cpu.vectors(p)

# Subr R(4)
#p.todo(0x0644, p.cpu.disass)
#x = p.t.add(0x0644,0x0654, "subr")
#p.setlabel(0x0644, "SUBR R(4)")

# Subr R(5)
#p.todo(0x0654, p.cpu.disass)
#x = p.t.add(0x0654,0x0661, "subr")
#p.setlabel(0x0654, "SUBR R(5)")

p.setlabel(0x06b9, "R15 = (R13++)")
p.setlabel(0x06be, "(R13++) = R15")
p.setlabel(0x06c5, "R15 = -R15")

while p.run():
	pass

p.build_bb()
p.build_procs()

def model_set(p, input, reg, val):
	if reg == "/R(P)":
		assert val[0] == 16
		reg_p = input["/P"]
		if reg_p[1] == None:
			return
		idx = "/R%d" % reg_p[1]
		assert input[idx][0] == val[0]
		input[idx] = val
		return
	if reg == "/R(X)":
		assert val[0] == 16
		reg_x = input["/X"]
		if reg_x[1] == None:
			return
		idx = "/R%d" % reg_x[1]
		assert input[idx][0] == val[0]
		input[idx] = val
		return
	elif reg in input:
		assert val[0] == input[reg][0]
		input[reg] = val
		return

	print("### unknown register (set)", reg)
	exit (0)

def model_get(p, input, reg):
	if reg == "/R(X)":
		reg_x = input["/X"]
		if reg_x[1] == None:
			return (16, None)
		return input["/R%d" % reg_x[1]]

	if reg == "/R(P)":
		reg_p = input["/P"]
		if reg_p[1] == None:
			return (16, None)
		return input["/R%d" % reg_p[1]]

	print("### unknown register (get)", reg)
	exit (0)
	return (0, None)

import copy

def model_eval(p, model, input, ind = ""):
	if False:
		print("")
		print(ind, "Model:", type(model))
		if type(model) == tuple:
			for i in model:
				print(ind, "\t",i)
		else:
			print(ind, "\t",model)

	if False:
		print(ind, "Input:")
		s = ""
		for i in input:
			if input[i][1] != None:
				s += " " + i + ":" + str(input[i])
		print(ind, "\t",s)


	if model[0] == "/":
		return model_get(p, input, model)
	if model[0] == "#":
		# XXX: Width
		return (16, int(model[1:]))
	if model[0] == "SEQ":
		for i in model[1:]:
			model_eval(p, i, input, ind + "\t")
		return (None)
	elif model[0] == ">>":
		v1 = model_eval(p, model[1], input, ind + "\t")
		v2 = model_eval(p, model[2], input, ind + "\t")
		assert v2[1] != None
		if v1[1] == None:
			return(v1[0], None)
		return(v1[0], v1[1] >> v2[1])
	elif model[0] == "TRIM":
		v1 = model_eval(p, model[1], input, ind + "\t")
		v2 = model_eval(p, model[2], input, ind + "\t")
		assert v2[1] != None
		if v1[1] == None:
			return(v2[1], None)
		return(v2[1], v1[1] & ((1 << v2[1]) - 1))
	elif model[0] == "MEM":
		v = model_eval(p, model[1], input, ind + "\t")
		if v[1] != None:
			return (8, p.m.rd(v[1]))
		return (8, None)
	elif model[0] == "INC":
		v = model_eval(p, model[1], input, ind + "\t")
		if v[1] != None:
			v = (v[0], v[1] + 1)
		model_set(p, input, model[1], v)
	elif model[0] == "=":
		v = model_eval(p, model[2], input, ind + "\t")
		model_set(p, input, model[1], v)
	elif model[0] == "DISASS":
		v = model_eval(p, model[1], input, ind + "\t")
		# XXX: Set flow on ins
		# XXX: Set model_in on next ins
		if v[1] != None:
			p.todo(v[1], p.cpu.disass)
	else:
		print(ind, "Unknown verb", model[0])
		print(ind, "Model:", model)
		print(ind, "Input:", input)
		exit (0)

def model(t, p, lvl):
	if not 'model' in t.a:
		return

	t.a['model_in'] = {
		"/I": (4, 0),
		"/N": (4, 0),
		"/Q": (1, 0),
		"/P": (4, 0),
		"/X": (4, 0),
		"/IE": (1, 1),
		"/R0": (16, 0),
		"/R1": (16, None),
		"/R2": (16, None),
		"/R3": (16, None),
		"/R4": (16, None),
		"/R5": (16, None),
		"/R6": (16, None),
		"/R7": (16, None),
		"/R8": (16, None),
		"/R9": (16, None),
		"/R10": (16, None),
		"/R11": (16, None),
		"/R12": (16, None),
		"/R13": (16, None),
		"/R14": (16, None),
		"/R15": (16, None),
	}

	input = t.a['model_in']

	output = copy.deepcopy(input)
	print(t.a['model'])
	model_eval(p, t.a['model'], output)
	t.a['model_out'] = output
	t.cmt.append("Model in: " + str(input))
	for i in input:
		assert input[i][0] == output[i][0]
		if input[i][1] != output[i][1]:
			t.cmt.append("Model output: " + i + " -> " + str(output[i]))
p.t.recurse(model, p)

while p.run():
	pass


p.render("/tmp/_cdp1802.bin")


