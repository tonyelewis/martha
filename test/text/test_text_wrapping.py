import pytest

import blessed  # type: ignore[import]

from text.display_text import DisplayText
from text.text_wrapping import constrained_to_text_and_width, id_of_wrapped_line_after_wrapped_line, id_of_wrapped_line_before_line, id_of_wrapped_line_before_wrapped_line, last_wrapped_line_id_of_line_index
from text.wrap_width import WrapWidth
from text.wrapped_line_id import WrappedLineId


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


def test_last_wrapped_line_id_of_line_index(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth( 3 )
	assert last_wrapped_line_id_of_line_index( 0, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )
	assert last_wrapped_line_id_of_line_index( 1, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )
	assert last_wrapped_line_id_of_line_index( 2, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert last_wrapped_line_id_of_line_index( 3, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	with pytest.raises(IndexError):
		last_wrapped_line_id_of_line_index( 4, text=eg_disp_text, wrap_width=ww )

	assert last_wrapped_line_id_of_line_index( 0, text=one_empty_line_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	with pytest.raises(IndexError):
		last_wrapped_line_id_of_line_index( 1, text=one_empty_line_disp_text, wrap_width=ww )


def test_id_of_wrapped_line_before_line(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth( 3 )
	assert id_of_wrapped_line_before_line( 0, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	assert id_of_wrapped_line_before_line( 1, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )
	assert id_of_wrapped_line_before_line( 2, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )
	assert id_of_wrapped_line_before_line( 3, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert id_of_wrapped_line_before_line( 4, text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	with pytest.raises(IndexError):
		id_of_wrapped_line_before_line( 5, text=eg_disp_text, wrap_width=ww )

	assert id_of_wrapped_line_before_line( 0, text=one_empty_line_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	assert id_of_wrapped_line_before_line( 1, text=one_empty_line_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	with pytest.raises(IndexError):
		id_of_wrapped_line_before_line( 2, text=one_empty_line_disp_text, wrap_width=ww )


def test_constrained_to_text_and_width(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth( 3 )
	assert constrained_to_text_and_width( WrappedLineId( 0, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	assert constrained_to_text_and_width( WrappedLineId( 0, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 1 )
	assert constrained_to_text_and_width( WrappedLineId( 0, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )
	assert constrained_to_text_and_width( WrappedLineId( 0, 3 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )

	assert constrained_to_text_and_width( WrappedLineId( 1, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 0 )
	assert constrained_to_text_and_width( WrappedLineId( 1, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )
	assert constrained_to_text_and_width( WrappedLineId( 1, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )

	assert constrained_to_text_and_width( WrappedLineId( 2, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 0 )
	assert constrained_to_text_and_width( WrappedLineId( 2, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert constrained_to_text_and_width( WrappedLineId( 2, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )

	assert constrained_to_text_and_width( WrappedLineId( 3, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	assert constrained_to_text_and_width( WrappedLineId( 3, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )

	with pytest.raises(IndexError):
		constrained_to_text_and_width( WrappedLineId( 4, 0 ), text=eg_disp_text, wrap_width=ww )


def test_id_of_wrapped_line_before_wrapped_line(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth( 3 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 0, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 0, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 0 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 0, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 1 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 0, 3 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 1 )

	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 1, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 1, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 0 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 1, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 0 )

	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 2, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 2, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 0 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 2, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 0 )

	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 3, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 3, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert id_of_wrapped_line_before_wrapped_line( WrappedLineId( 3, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )

	with pytest.raises(IndexError):
		id_of_wrapped_line_before_wrapped_line( WrappedLineId( 4, 0 ), text=eg_disp_text, wrap_width=ww )


def test_id_of_wrapped_line_after_wrapped_line(eg_disp_text, one_empty_line_disp_text):
	ww = WrapWidth( 3 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 0, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 1 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 0, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 0, 2 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 0, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 0 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 0, 3 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 0 )

	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 1, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 1, 1 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 1, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 0 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 1, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 0 )

	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 2, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 2, 1 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 2, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 2, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )

	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 3, 0 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 3, 1 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )
	assert id_of_wrapped_line_after_wrapped_line( WrappedLineId( 3, 2 ), text=eg_disp_text, wrap_width=ww ) == WrappedLineId( 3, 0 )

	with pytest.raises(IndexError):
		id_of_wrapped_line_before_wrapped_line( WrappedLineId( 4, 0 ), text=eg_disp_text, wrap_width=ww )
