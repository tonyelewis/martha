import pytest

from pathlib import Path

from cppbuild.raw_dep_record import read_compiler_deps_file

TEST_DATA_DIR = Path(__file__).parent.resolve() / 'test-data'

EXAMPLE_DEPS_FILE = TEST_DATA_DIR / 'example.compiler-deps.txt'


def test_read_compiler_deps_file():
	the_deps = read_compiler_deps_file(
		EXAMPLE_DEPS_FILE,
		target=Path('source/options/options_block/pdb: input_spec.hpp'),
	)

	assert the_deps.target == Path(
		'source/options/options_block/pdb: input_spec.hpp')
	assert the_deps.is_valid == True
	assert len(the_deps.deps) == 431
	assert all(isinstance(x, Path) for x in the_deps.deps)
	assert Path('source/options/options_block/pdb: input_spec.hpp') in the_deps.deps
	assert Path('source/src common/common/path_type_aliases.hpp') in the_deps.deps
