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
	# TODOCUMENT: What exactly does this mean?
	is_valid: bool

	# The dependencies (roughly, the headers)
	#
	# TODO: Consider migrating these to strings to avoid the need to
	#       convert to Paths when they'll only then be used as lookups for an ID anyway
	deps: List[Path]


def parse_compiler_deps(compiler_deps_str: str) -> RawDepRecord:
	'''
	Parse dependencies as output by a compiler from the specified string

	:param compiler_deps_str: The string from which to parse the dependencies
	'''
	compiler_deps_str = compiler_deps_str.replace('\\\n', '')
	parts = shlex.split(compiler_deps_str)
	assert parts
	assert parts[0].endswith(':')
	return RawDepRecord(
		target=Path(parts[0][:-1]),
		is_valid=True,
		deps=[Path(x) for x in parts[1:]],
	)


def read_compiler_deps_file(compiler_deps_file: Path) -> RawDepRecord:
	'''
	Parse dependencies as output by a compiler from the specified file

	:param compiler_deps_file: The file from which to parse the dependencies
	'''
	with open(compiler_deps_file, 'r') as compiler_deps_fh:
		return parse_compiler_deps(compiler_deps_fh.read())
