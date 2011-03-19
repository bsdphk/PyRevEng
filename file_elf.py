#!/usr/local/bin/python
#
# ELF file handling
#

from __future__ import print_function

import sys
import struct

import mem

Elf32_Ehdr = (
	52,
	"16s H H I I I I I H H H H H H",
	(
		( "e_ident", ),
		( "e_type", {
			0: "ET_NONE",
			1: "ET_REL",
			2: "ET_EXEC",
			3: "ET_DYN",
			4: "ET_CORE",
			}
		),
		( "e_machine", {
			0: "EM_NONE",
			1: "EM_M32",
			2: "EM_SPARC",
			3: "EM_386",
			4: "EM_68K",
			5: "EM_88K",
			6: "EM_860",
			7: "EM_MIPS",
			}
		),
		( "e_version", {
			0: "EV_NONE",
			1: "EV_CURRENT",
			}
		),
		( "e_entry", ),
		( "e_phoff", ),
		( "e_shoff", ),
		( "e_flags", ),
		( "e_ehsize", ),
		( "e_phentsize", ),
		( "e_phnum", ),
		( "e_shentsize", ),
		( "e_shnum", ),
		( "e_shstrndx", ),
	)
)

Elf32_Shdr = (
	40,
	"I I I I I I I I I I",
	(
		( "sh_name", ),
		( "sh_type", {
			0: "SHT_NULL",
			1: "SHT_PROGBITS",
			2: "SHT_SYMTAB",
			3: "SHT_STRTAB",
			4: "SHT_RELA",
			5: "SHT_HASH",
			6: "SHT_DYNAMIC",
			7: "SHT_NOTE",
			8: "SHT_NOBITS",
			9: "SHT_REL",
			10: "SHT_SHLIB",
			11: "SHT_DYNSYM",
			}
		),
		( "sh_flags", ),
		( "sh_addr", ),
		( "sh_offset", ),
		( "sh_size", ),
		( "sh_link", ),
		( "sh_info", ),
		( "sh_addralign", ),
		( "sh_entsize", ),
	)
)

Elf32_Sym = (
	16,
	"I I I B B H",
	(
		( "st_name", ),
		( "st_value", ),
		( "st_size", ),
		( "st_info", ),
		( "st_other", ),
		( "st_shndx", ),
	)
)

class ElfError(Exception):
	def __init__(self, filename, reason):
		self.fn = filename
		self.reason = reason
		self.value = filename + ": " + reason
	def __str__(self):
		return repr(self.value)

class estruct(object):
	def __init__(self, sspec, endian,ptr, off):
		t = str(ptr[off:off+sspec[0]])
		l = struct.unpack(endian + sspec[1], t)
		n = 0
		for i in sspec[2]:
			v = l[n]
			if len(i) == 2:
				if v in i[1]:
					v = i[1][v]
			self.__setattr__(i[0], v)
			n += 1
		self.flds = sspec[2]

	def print(self, f=sys.stdout):
		for i in self.flds:
			v = self.__dict__[i[0]]
			if v != 0:
				f.write("%-20s" % i[0] + " " + str(v) + "\n")

class elf(object):
	def __init__(self, filename):

		# Read the entire file
		f = open(filename, "rb")
		self.d = bytearray(f.read())

		# Check Ident
		if self.d[0] != 0x7f or self.d[1:4] != "ELF":
			raise ElfError(filename, "ELF magic not '\x7fELF'")

		# Determine size
		if self.d[4] == 1:
			self.ei_class = 32
		else:
			raise ElfError(filename, "bad/unsupported ELF class")

		# Determine endianess
		if self.d[5] == 1:
			self.endian = "<"
		elif self.d[4] == 2:
			self.endian = ">"
		else:
			raise ElfError(filename, "bad ELF endianess")

		# Determine size
		if self.d[6] != 1:
			raise ElfError(filename, "bad/unsupported ELF version")

		# Read Section Headers
		self.e_hdr = estruct(Elf32_Ehdr, self.endian, self.d, 0)
		self.e_sh = []
		for i in range(0,self.e_hdr.e_shnum):
			sh = estruct(
			    Elf32_Shdr,
			    self.endian,
			    self.d,
			    self.e_hdr.e_shoff + i * self.e_hdr.e_shentsize)
			self.e_sh.append(sh)

		self.shstrtab = self.e_sh[self.e_hdr.e_shstrndx]
		if self.shstrtab.sh_type != "SHT_STRTAB":
			raise ElfError(filename,
			    "String section has wrong type")

		# Patch up subsection names
		for i in self.e_sh:
			nm = self.elfstr(i.sh_name, self.shstrtab)
			i.__setattr__("sh_name", nm)

		# Find symbol table, if any
		self.symtab = None
		self.strtab = None
		for i in self.e_sh:
			if i.sh_type == "SHT_SYMTAB":
				self.symtab = i
			if i.sh_name == ".strtab":
				self.strtab = i

		# Read symbols
		self.syms = list()
		self.symbyname = dict()
		for j in range(0, self.symtab.sh_size, Elf32_Sym[0]):
			ss = estruct(Elf32_Sym,
			    self.endian,
			    self.d,
			    self.symtab.sh_offset + j)
			nm = self.elfstr(ss.st_name, self.strtab)
			ss.__setattr__("st_name", nm)

			stb = ss.st_info >> 4
			assert stb >= 0 and stb <= 15
			i1 = ("STB_LOCAL", "STB_GLOBAL", "STB_WEAK")[stb]

			stt = ss.st_info & 0xf
			i2 = ("STT_NOTYPE", "STT_OBJECT", "STT_FUNC",
			    "STT_SECTION", "STT_FILE")[stt]

			ss.__setattr__("st_info", (i1, i2))
		
			self.syms.append(ss)
			if nm != "":
				self.symbyname[str(nm)] = ss
		
	def elfstr(self, off, sec):
		if off < 0 or off >= sec.sh_size:
			raise ElfError(filename, "Invalid string index")
		p = sec.sh_offset + off
		for i in range(0, sec.sh_size-off):
			if self.d[p + i] == 0:
				break
		return self.d[p:p+i]

	def load_size(self):
		# Make list of sections we will load.
		l=list()
		sz = 0
		for i in self.e_sh:
			if i.sh_size == 0:
				continue
			if not i.sh_flags & 0x2:
				continue
			if i.sh_type == "SHT_PROGBITS":
				l.append(i)
				sz += i.sh_size
				i.print()
			if i.sh_type == "SHT_NOBITS":
				l.append(i)
				sz += i.sh_size
				i.print()
		print(sz)
		ss = 0x10
		for i in l:
			while i.sh_size > ss:
				ss <<= 4
		return(l, ss, sz)

	def load_mem(self):
		l,ss,sz = self.load_size()
		m = mem.byte_mem(end = len(l) * ss, endian = self.endian,
		    flags=True)
		return m

	def load(self, p):
		l,ss,sz = self.load_size()
		m = p.m
		ba = 0
		for i in l:
			print(i.sh_name)
			if i.sh_type == "SHT_PROGBITS":
				for j in range(0, i.sh_size):
					m.setflags(ba + j, None,
					    m.can_read|m.can_write,
					    m.invalid|m.undef)
					m.wr(ba + j, self.d[i.sh_offset + j])
			p.t.add(ba, ba + i.sh_size, "section " + i.sh_name)
			ba += ss

if __name__ == "__main__":
	try:
		e = elf("file_elf.py")
	except:
		pass
	e = elf("Soekris/hda.o")
	#e = elf("Soekris/cpu_nb_basic_init_memory.o")

	if True:
		print("ELF header")
		e.e_hdr.print()
		n=0
		for i in e.e_sh:
			print("\nSubSection[%d]" % n, i.sh_name)
			n += 1
			i.print()
		for i in e.syms:
			print("\nSymbol(%s)" % i.st_name)
			i.print()
