#!/usr/local/bin/python

def hint(p):
	cpu = p.c["domus"]
	cpu.disass(0o100013)
	cpu.disass(0o100025)
	cpu.disass(0o100026)
	cpu.disass(0o100017)
	cpu.disass(0o100034)
	
