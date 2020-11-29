import shlex

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class RawDepRecord:
	'''
	A dependency record from the compiler (roughly a description of the headers used in compiling a specific cpp file)

	This may come from ninja or directly from the compiler.

	It is raw in the sense that it contains the actual filenames rather than looked-up IDs
	'''

	# The target (roughly, the cpp file)
	target: Path

	# is_valid as reported by ninja
	#
	# It isn't fully clear what this means.
	# Values seen so far: VALID, STALE.
	# STALE occurs if the object file no long exists but doesn't occur if the source files are touched.
	is_valid: bool

	# The dependencies (roughly, the headers)
	#
	# TODO: Consider migrating these to strings to avoid the need to
	#       convert to Paths when they'll only then be used as lookups for an ID anyway
	deps: List[Path]


def parse_compiler_deps(compiler_deps_str: str, *, target: Path) -> RawDepRecord:
	'''
	Parse dependencies as output by a compiler from the specified string

	The target must be specified to disambiguate the initial line
	(eg does `fred.cpp: mary.cpp:` refer to two files (`fred.cpp`,  `mary.cpp:`) or one (`fred.cpp: mary.cpp`:))

	:param compiler_deps_str : The string from which to parse the dependencies
	:param target            : The target being compiled (must exactly match the initial deps entry)
	'''
	assert compiler_deps_str.startswith( f'{target}: ' )
	deps_str = compiler_deps_str[len(str(target))+1:]
	deps_str = deps_str.replace('\\\n', '')
	deps = shlex.split(deps_str)
	return RawDepRecord(
		target=target,
		is_valid=True,
		deps=[Path(x) for x in deps],
	)


def read_compiler_deps_file(compiler_deps_file: Path, *, target: Path) -> RawDepRecord:
	'''
	Parse dependencies as output by a compiler from the specified file

	:param compiler_deps_file : The file from which to parse the dependencies
	:param target             : The target being compiled (must exactly match the initial deps entry)
	'''
	with open(compiler_deps_file, 'r') as compiler_deps_fh:
		return parse_compiler_deps(
			compiler_deps_str=compiler_deps_fh.read(),
			target=target,
		)
