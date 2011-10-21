#!/usr/local/bin/python
#
# This is a "real" task which disassembles DOMUS relocatable binaries
# from RC3600 or RC7000 DOMUS systems.
#
# If you have never heard of either, you're not alone.
#
# RegneCentralen was a Danish computer manufacturer.
# The RC7000 computer were a rebadged Data General Nova.
# The RC3600 was a re-engineered version built in Denmark.
# More info: http://www.datamuseum.dk
#
# The reason this is a good test-case for PyRevEng is that it typically
# are pretty small programs, the OS is well documented and, most importantly,
# may of the programs contain interpreted code, for the "MUSIL" language.
#
# I have included the "CATLI" program here, it produces a "CATalog LIst",
# of the filesystem.
#
# Yell at me if you want docs for this platforms, we have tons of pdfs.

#----------------------------------------------------------------------
# Check the python version

import sys
assert sys.version_info[0] >= 3 or "Need" == "Python v3"

#----------------------------------------------------------------------
# Set up a search path to two levels below
# XXX: There must be a better way than this gunk...

import os
sys.path.insert(0, "/".join(os.getcwd().split("/")[:-2]))

#----------------------------------------------------------------------
# Stuff we need...

import domus.do_file
import domus.inter.inter as inter

print(sys.argv)

targets = ("__.CATLI",)

if len(sys.argv) > 1:
	targets = sys.argv[1:]

for tf in targets:
	print("Target: ", tf)
	load_file = domus.do_file.find_file(tf)

	oi = load_file.build_index()

	for obj in oi:
		p = domus.do_file.load_obj(load_file, obj)
		i = inter.inter(p)

		domus.do_file.auto_magic(p)
		domus.do_file.auto_hints(p)

		domus.do_file.finish(p)
