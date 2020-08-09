import pytest

from pathlib import Path

from cppbuild.dir_tools import WorkingDirChange, from_changed_working_dir


def test_working_dir_change_throws_on_mismatching_absoluteness():
	with pytest.raises(ValueError):
		WorkingDirChange( prev_working_dir=Path( '/b' ), new_working_dir=Path(  'a' ) )

	with pytest.raises(ValueError):
		WorkingDirChange( prev_working_dir=Path( 'b'  ), new_working_dir=Path( '/a' ) )


def test_from_changed_working_dir():
	assert from_changed_working_dir(Path(    'b/c' ), WorkingDirChange( prev_working_dir=Path( '/b' ), new_working_dir=Path( '/b/b' ) ) ) == Path( 'c'      )
	assert from_changed_working_dir(Path(    'b/c' ), WorkingDirChange( prev_working_dir=Path(  'b' ), new_working_dir=Path(  'b/b' ) ) ) == Path( 'c'      )
	assert from_changed_working_dir(Path( '/a/b/c' ), WorkingDirChange( prev_working_dir=Path( '/a' ), new_working_dir=Path( '/a/b' ) ) ) == Path( '/a/b/c' )
	assert from_changed_working_dir(Path( '/a/b/c' ), WorkingDirChange( prev_working_dir=Path(  'a' ), new_working_dir=Path(  'a/b' ) ) ) == Path( '/a/b/c' )

