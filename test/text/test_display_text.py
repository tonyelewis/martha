import pytest

import blessed

from text.display_text import DisplayText


def test_display_text():
	dt = DisplayText(
		'here is\n\x1b[00m\x1b[01;31msome\ntext\x1b[00m\n\x1b[01;31m',
		term=blessed.Terminal()
	)
	assert dt.lines == [
		'here is',
		'\x1b[00m\x1b[01;31msome',
		'text\x1b[00m',
		'\x1b[01;31m'
	]
	assert dt.line_term_lengths == [7, 4, 4, 0]
