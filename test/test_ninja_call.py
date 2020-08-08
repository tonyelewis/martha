import pytest

from pathlib import Path

from cppbuild.ninja_call import NinjaCompDBRecord, compdb_of_compdb_str, get_ninja_deps_str_for_dir, project_dir_of_compdb


TEST_DATA_DIR = Path(__file__).parent.resolve() / 'test-data'

EG_COMPDB_STR = '''[
	{
		"directory": "/project/ninja_clang_rwdi",
		"command": "",
		"file": "some-exe",
		"output": "source/all"
	},
	{
		"directory": "/project/ninja_clang_rwdi",
		"command": "/usr/bin/cmake -S/project -B/project/ninja_clang_rwdi",
		"file": "../CMakeLists.txt",
		"output": "build.ninja"
	}
]'''

EG_COMPDB = [
		NinjaCompDBRecord(
			directory=Path('/project/ninja_clang_rwdi'),
			command='',
			file=Path('some-exe'),
			output='source/all'
		),
		NinjaCompDBRecord(
			directory=Path('/project/ninja_clang_rwdi'),
			command='/usr/bin/cmake -S/project -B/project/ninja_clang_rwdi',
			file=Path('../CMakeLists.txt'),
			output='build.ninja'
		),
]


def test_compdb_of_compdb_str():
	assert compdb_of_compdb_str(EG_COMPDB_STR) == EG_COMPDB


def test_project_dir_of_compdb():
	assert project_dir_of_compdb(EG_COMPDB) == Path('/project')


def test_project_dir_of_compdb_raises_value_error_if_not_found():
	with pytest.raises(ValueError):
		project_dir_of_compdb([])
