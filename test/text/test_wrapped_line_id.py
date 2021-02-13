import pytest

from text.wrapped_line_id import WrappedLineId, decremented_wrapped_line_offset_copy, incremented_wrapped_line_offset_copy


def test_ctor():
	assert WrappedLineId() == WrappedLineId(
		line_index=0,
		wrapped_line_offset=0,
	)
	assert WrappedLineId(3, 5) == WrappedLineId(
		line_index=3,
		wrapped_line_offset=5,
	)


def test_decremented_wrapped_line_offset_copy():
	assert decremented_wrapped_line_offset_copy( WrappedLineId( 3, 14 ) ) == WrappedLineId( 3, 13 )
	assert decremented_wrapped_line_offset_copy( WrappedLineId( 3,  1 ) ) == WrappedLineId( 3,  0 )
	assert decremented_wrapped_line_offset_copy( WrappedLineId( 3,  0 ) ) == WrappedLineId( 3,  0 )


def test_incremented_wrapped_line_offset_copy():
	assert incremented_wrapped_line_offset_copy( WrappedLineId( 3, 14 ) ) == WrappedLineId( 3, 15 )
