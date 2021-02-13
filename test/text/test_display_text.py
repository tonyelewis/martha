import pytest

import blessed  # type: ignore[import]

from text.display_text import DisplayText, index_of_last_line, last_wrapped_line_num_of_length, last_wrapped_line_num_of_line, num_wrapped_lines_of_length, num_wrapped_lines_of_line
from text.wrap_width import WrapWidth


@pytest.fixture
def eg_disp_text():
	return DisplayText(
		'here is\n\x1b[00m\x1b[01;31msome\ntext\x1b[00m\n\x1b[01;31m',
		term=blessed.Terminal()
	)


@pytest.fixture
def one_empty_line_disp_text():
	return DisplayText(
		'',
		term=blessed.Terminal()
	)


def test_last_wrapped_line_num_of_length():
	ww = WrapWidth(4)
	assert last_wrapped_line_num_of_length(0, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_length(1, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_length(2, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_length(3, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_length(4, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_length(5, wrap_width=ww) == 1
	assert last_wrapped_line_num_of_length(6, wrap_width=ww) == 1
	assert last_wrapped_line_num_of_length(7, wrap_width=ww) == 1


def test_num_wrapped_lines_of_length():
	ww = WrapWidth(4)
	assert num_wrapped_lines_of_length(0, wrap_width=ww) == 1
	assert num_wrapped_lines_of_length(1, wrap_width=ww) == 1
	assert num_wrapped_lines_of_length(2, wrap_width=ww) == 1
	assert num_wrapped_lines_of_length(3, wrap_width=ww) == 1
	assert num_wrapped_lines_of_length(4, wrap_width=ww) == 1
	assert num_wrapped_lines_of_length(5, wrap_width=ww) == 2
	assert num_wrapped_lines_of_length(6, wrap_width=ww) == 2
	assert num_wrapped_lines_of_length(7, wrap_width=ww) == 2


def test_display_text_getters(eg_disp_text, one_empty_line_disp_text):
	assert eg_disp_text.lines == [
		'here is',
		'\x1b[00m\x1b[01;31msome',
		'text\x1b[00m',
		'\x1b[01;31m'
	]
	assert eg_disp_text.line_term_lengths == [7, 4, 4, 0]

	assert one_empty_line_disp_text.lines == ['']
	assert one_empty_line_disp_text.line_term_lengths == [0]


def test_num_term_wrapped_lines_of_line(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth(4)
	assert num_wrapped_lines_of_line(eg_disp_text, line_index=0, wrap_width=ww) == 2
	assert num_wrapped_lines_of_line(eg_disp_text, line_index=1, wrap_width=ww) == 1
	assert num_wrapped_lines_of_line(eg_disp_text, line_index=2, wrap_width=ww) == 1
	assert num_wrapped_lines_of_line(eg_disp_text, line_index=3, wrap_width=ww) == 1

	assert num_wrapped_lines_of_line(one_empty_line_disp_text, line_index=0, wrap_width=ww) == 1


def test_last_wrapped_line_num_of_line(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth(4)
	assert last_wrapped_line_num_of_line(
		eg_disp_text, line_index=0, wrap_width=ww) == 1
	assert last_wrapped_line_num_of_line(
		eg_disp_text, line_index=1, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_line(
		eg_disp_text, line_index=2, wrap_width=ww) == 0
	assert last_wrapped_line_num_of_line(
		eg_disp_text, line_index=3, wrap_width=ww) == 0
	with pytest.raises(IndexError):
		last_wrapped_line_num_of_line(eg_disp_text, line_index=4, wrap_width=ww)

	assert last_wrapped_line_num_of_line(
		one_empty_line_disp_text, line_index=0, wrap_width=ww) == 0
	with pytest.raises(IndexError):
		last_wrapped_line_num_of_line(one_empty_line_disp_text, line_index=1, wrap_width=ww)


def test_index_of_last_line(eg_disp_text, one_empty_line_disp_text):
	assert index_of_last_line(eg_disp_text) == 3
	assert index_of_last_line(one_empty_line_disp_text) == 0
