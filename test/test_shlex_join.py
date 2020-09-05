import pytest

from cppbuild.shlex_join import shlex_join_shim


def test_shlex_join_shim():
	command = [
		'a"a',
		"b'b"
		R'\!£$%^&*()_+-=[]{};#:@~,./,./',
	]
	assert shlex_join_shim(
		command) == '\'a"a\' \'b\'"\'"\'b\\!£$%^&*()_+-=[]{};#:@~,./,./\''
	assert shlex_join_shim(
		command, '#') == '\'a"a\'#\'b\'"\'"\'b\\!£$%^&*()_+-=[]{};#:@~,./,./\''
