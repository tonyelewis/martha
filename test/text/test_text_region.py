import pytest

import blessed  # type: ignore[import]

from text.display_text import DisplayText
from text.text_region import add_wrapped_line_offset, term_printable_substring, wrapped_line_ranges_between, wrapped_lines_region_of
from text.wrap_width import WrapWidth
from text.wrapped_line_id import WrappedLineId

def test_term_printable_substring():
	term = blessed.Terminal()
	assert term_printable_substring( 'hello', 1, 3, term=term ) == 'el'
	assert term_printable_substring( 'hello', 1, 1, term=term ) == ''

	with pytest.raises(ValueError):
		term_printable_substring( 'hello', 2, 1, term=term )


def test_term_printable_substring_handles_sequences():
	term = blessed.Terminal()
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  0,  2, term=term ) == 'he'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  1,  3, term=term ) == 'er'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  2,  4, term=term ) == 're'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  3,  5, term=term ) == 'e '
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  4,  6, term=term ) == ' i'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  5,  7, term=term ) == 'is\x1b[00m\x1b[01;31m'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  6,  8, term=term ) == 's\x1b[00m\x1b[01;31ma'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  7,  9, term=term ) == '\x1b[00m\x1b[01;31ma '
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  8, 10, term=term ) == '\x1b[00m\x1b[01;31m t'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!',  9, 11, term=term ) == '\x1b[00m\x1b[01;31mte'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!', 10, 12, term=term ) == '\x1b[00m\x1b[01;31mex'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!', 11, 13, term=term ) == '\x1b[00m\x1b[01;31mxt\x1b[00m\x1b[01;31m'
	assert term_printable_substring( 'here is\x1b[00m\x1b[01;31ma text\x1b[00m\x1b[01;31m!', 12, 14, term=term ) == '\x1b[00m\x1b[01;31mt\x1b[00m\x1b[01;31m!'


def test_first_wrapped_line_after():
	term = blessed.Terminal()
	dt = DisplayText( 'boo\nwe are\nin far\nnow', term=term )
	ww = WrapWidth(3)
	lines = (
		WrappedLineId(0,0),
		WrappedLineId(1,0),
		WrappedLineId(1,1),
		WrappedLineId(2,0),
		WrappedLineId(2,1),
		WrappedLineId(3,0),
		WrappedLineId(4,0),
	)
	for line_index_a, line_a in enumerate(lines):
		for line_index_b, line_b in enumerate(lines):
			assert add_wrapped_line_offset(line_a, line_index_b-line_index_a, text=dt, wrap_width=ww) == line_b

	assert add_wrapped_line_offset(WrappedLineId(2,0), -20, text=dt, wrap_width=ww) == WrappedLineId(0,0)
	assert add_wrapped_line_offset(WrappedLineId(2,0),  20, text=dt, wrap_width=ww) == WrappedLineId(4,0)


def test_wrapped_line_ranges_between():
	ltls = [7, 0, 4, 4, 0]
	ww = WrapWidth(3)
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 0), end_id=WrappedLineId(0, 2), line_term_lengths=ltls, wrap_width=ww) == 'here i'
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 1), end_id=WrappedLineId(1, 0), line_term_lengths=ltls, wrap_width=ww) == 'e is'
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 2), end_id=WrappedLineId(2, 0), line_term_lengths=ltls, wrap_width=ww) == 's\n'
	wrapped_line_ranges_between(begin_id=WrappedLineId(1, 0), end_id=WrappedLineId(2, 1), line_term_lengths=ltls, wrap_width=ww) == '\n\x1b[00m\x1b[01;31msom'
	wrapped_line_ranges_between(begin_id=WrappedLineId(2, 0), end_id=WrappedLineId(3, 0), line_term_lengths=ltls, wrap_width=ww) == '\x1b[00m\x1b[01;31msome'
	wrapped_line_ranges_between(begin_id=WrappedLineId(2, 1), end_id=WrappedLineId(3, 1), line_term_lengths=ltls, wrap_width=ww) == '\x1b[00m\x1b[01;31me\ntex' # + term.normal
	wrapped_line_ranges_between(begin_id=WrappedLineId(3, 0), end_id=WrappedLineId(4, 0), line_term_lengths=ltls, wrap_width=ww) == 'text\x1b[00m'
	wrapped_line_ranges_between(begin_id=WrappedLineId(3, 1), end_id=WrappedLineId(5, 0), line_term_lengths=ltls, wrap_width=ww) == 't\x1b[00m\n\x1b[01;31m'
	wrapped_line_ranges_between(begin_id=WrappedLineId(4, 0), end_id=WrappedLineId(5, 0), line_term_lengths=ltls, wrap_width=ww) == '\x1b[01;31m'
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 0), end_id=WrappedLineId(0, 0), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 1), end_id=WrappedLineId(0, 1), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(0, 2), end_id=WrappedLineId(0, 2), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(1, 0), end_id=WrappedLineId(1, 0), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(2, 0), end_id=WrappedLineId(2, 0), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(2, 1), end_id=WrappedLineId(2, 1), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(3, 0), end_id=WrappedLineId(3, 0), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(3, 1), end_id=WrappedLineId(3, 1), line_term_lengths=ltls, wrap_width=ww) == ''
	wrapped_line_ranges_between(begin_id=WrappedLineId(4, 0), end_id=WrappedLineId(4, 0), line_term_lengths=ltls, wrap_width=ww) == ''


def test_wrapped_lines_region_of():
	term = blessed.Terminal()
	dt = DisplayText( 'here is\n\n\x1b[00m\x1b[01;31msome\ntext\x1b[00m\n\x1b[01;31m', term=term )
	ww = WrapWidth(3)

	# here is                   0 'her'                        'e i'               's'
	# \x1b[00m\x1b[01;31msome   1 ''
	# \x1b[00m\x1b[01;31msome   2 '\x1b[00m\x1b[01;31msom'     'e'
	# text\x1b[00m              3 'tex'                        't\x1b[00m'
	# \x1b[01;31m               4 '\x1b[01;31m'

	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 0), max_num_wrapped_lines=2, wrap_width=ww ) == 'here i'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 1), max_num_wrapped_lines=2, wrap_width=ww ) == 'e is'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 2), max_num_wrapped_lines=2, wrap_width=ww ) == 's\n'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(1, 0), max_num_wrapped_lines=2, wrap_width=ww ) == '\n\x1b[00m\x1b[01;31msom'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(2, 0), max_num_wrapped_lines=2, wrap_width=ww ) == '\x1b[00m\x1b[01;31msome'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(2, 1), max_num_wrapped_lines=2, wrap_width=ww ) == '\x1b[00m\x1b[01;31me\ntex' # + term.normal
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(3, 0), max_num_wrapped_lines=2, wrap_width=ww ) == 'text\x1b[00m'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(3, 1), max_num_wrapped_lines=2, wrap_width=ww ) == 't\x1b[00m\n\x1b[01;31m'
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(4, 0), max_num_wrapped_lines=2, wrap_width=ww ) == '\x1b[01;31m'

	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 0), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 1), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(0, 2), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(1, 0), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(2, 0), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(2, 1), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(3, 0), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(3, 1), max_num_wrapped_lines=0, wrap_width=ww ) == ''
	assert wrapped_lines_region_of(dt, term=term, begin_id=WrappedLineId(4, 0), max_num_wrapped_lines=0, wrap_width=ww ) == ''