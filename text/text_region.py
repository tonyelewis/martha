import bisect
import dataclasses
import itertools

from typing import Iterable, Iterator, List, Tuple, Optional

import blessed  # type: ignore[import]

from text.display_text import DisplayText, num_wrapped_lines_of_length
from text.wrap_width import WrapWidth
from text.wrapped_line_id import WrappedLineId

def term_printable_substring(line: str,
                             begin_printable_index: int,
                             end_printable_index: int,
                             *,
                             term: blessed.Terminal = blessed.Terminal(),
                             ) -> str:
	'''
	A string corresponding to the specified begin/(one-past) end indices into the specified line as it appears in the terminal,
	preserving any preceding terminal escape sequences

	This is greedy wrt including non-printing sequences at both ends

	:param line                  : The line of text to substring
	:param begin_printable_index : The begin index into the printable string
	:param end_printable_index   : The (one-past) end index into the printable string
	:param term                  : The blessed.Terminal to use to calculate the lengths
	'''
	if begin_printable_index > end_printable_index:
		raise ValueError('begin_printable_index cannot be greater than end_printable_index')

	# Break the line up into characters and sequences, and calculate the cumulative lengths
	# (by Python string len() and by terminal display length)
	# up to each of the boundaries of the parts
	#
	# TODO: Once the fix for https://github.com/python/typeshed/issues/4888 has propagated out, remove the `type: ignore[call-overload]`
	parts                       = term.split_seqs(line)
	cum_lengths:      List[int] = list(itertools.accumulate((len(x)         for x in parts), initial=0)) # type: ignore[call-overload]
	cum_term_lengths: List[int] = list(itertools.accumulate((term.length(x) for x in parts), initial=0)) # type: ignore[call-overload]

	# Get the (earliest/latest) indices of parts for which the corresponding cumulative display length matches begin_printable_index/end_printable_index
	parts_begin_index = bisect.bisect_left( cum_term_lengths, begin_printable_index)
	parts_end_index = bisect.bisect_right( cum_term_lengths, end_printable_index, lo=parts_begin_index) - 1

	return (
		# Return any sequences before the selected substring
		''.join(x for x in parts[:parts_begin_index] if x.startswith('\x1b'))
		# ...and the selected substring
		+ line[cum_lengths[parts_begin_index]:cum_lengths[parts_end_index]]
	)


def _num_wrapped_lines_by_end( disp_text: DisplayText,
                               *,
                               wrap_width: WrapWidth
                               ) -> List[int]:
	'''
	The number of wrapped lines that the specified text completes by the end of each of the full lines

	:param disp_text  : The text of interest
	:param wrap_width : The width at which lines are wrapped
	'''
	# TODO: Once the fix for https://github.com/python/typeshed/issues/4888 has propagated out, remove the `type: ignore[call-overload]`
	return list(itertools.accumulate(
		num_wrapped_lines_of_length( x, wrap_width=wrap_width ) for x in disp_text.line_term_lengths
	)) # type: ignore[call-overload]


def _wrapped_line_index_of_id( id: WrappedLineId,
                               *,
                               num_wrapped_lines_by_end: List[int],
                               ) -> int:
	'''
	The index of the wrapped line identified by the specified WrappedLineId

	Requires wrapped_line_id to be an valid ID of a wrapped line wrap_width, or WrappedLineId(num_lines, 0)

	:param id                       : The WrappedLineId of the wrapped-line of interest
	:param num_wrapped_lines_by_end : The number of wrapped lines that are completed by the end of each of the full lines
	'''
	return id.wrapped_line_offset + (
		0 if id.line_index == 0 else num_wrapped_lines_by_end[id.line_index-1]
	 )


def _wrapped_line_id_of_index( index: int,
                               *,
                               num_wrapped_lines_by_end: List[int],
                               min_full_line_index: int,
                               max_full_line_index: int,
                               ) -> WrappedLineId:
	'''
	The WrappedLineId corresponding to the index-th wrapped line in the text described by
	num_wrapped_lines_by_end, where the answer is known to be between min_full_line_index
	and max_full_line_index inclusive

	Clamps to a valid WrappedLineId for the num_wrapped_lines_by_end, or WrappedLineId(num_lines, 0)

	:param index                    : The wrapped-line-index of interest
	:param num_wrapped_lines_by_end : The number of wrapped lines that are completed by the end of each of the full lines
	:param min_full_line_index      : The minimum that the full_line_index might be
	:param max_full_line_index      : The maximum that the full_line_index might be
	'''
	if index < 0:
		return WrappedLineId(0, 0)

	# Find the index of the first full line that has more than the specified number of wrapped lines by its end
	# (or num_lines if no such line exists)
	#
	# bisect_right makes more sense here to achieve that "more than"; we want to get the same index out for
	# exact value matches as for the intermediate values _above_ (eg if the first two full lines both wrap to
	# three lines each, we want the groups of inputs that get the same answer to be [0,1,2] [3,4,5] [≥6]
	# not [0] [1,2,3] [4,5,≥6])
	full_line_index = bisect.bisect_right(
		num_wrapped_lines_by_end,
		index,
		lo=min_full_line_index,
		# hi=max_full_line_index,
	)
	if full_line_index > max_full_line_index:
		print()
		print( f'{index=}' )
		print( f'{num_wrapped_lines_by_end=}' )
		print( f'{min_full_line_index=}' )
		print( f'{max_full_line_index=}' )
		print( f'{full_line_index=}' )

	# Return a WrappedLineId for full_line_index and however many more lines are required to get to index
	# (clamping to a valid WrappedLineId for the num_wrapped_lines_by_end, or WrappedLineId(num_lines, 0)
	wrapped_lines_before_full_line: int = _wrapped_line_index_of_id(
		WrappedLineId(full_line_index,0),
		num_wrapped_lines_by_end=num_wrapped_lines_by_end
	)
	return WrappedLineId(
		line_index=full_line_index,
		wrapped_line_offset=min(num_wrapped_lines_by_end[-1], index) - wrapped_lines_before_full_line,
	)


def add_wrapped_line_offset( wrapped_line_id: WrappedLineId,
                             offset: int,
                             *,
                             text: DisplayText,
                             wrap_width: WrapWidth,
                             ) -> WrappedLineId:
	'''
	The result of adding the specified offset number of wrapped lines to the specified WrappedLineId
	in the specified text using the specified wrap-width

	Requires wrapped_line_id to be an valid ID of a wrapped line wrap_width, or WrappedLineId(num_lines, 0)

	Clamps the result to a valid WrappedLineId for the text and wrap_width, or WrappedLineId(num_lines, 0)

	:param wrapped_line_id : The ID if the initial lines
	:param offset          : The offset (number of wrapped lines) to add. May be negative.
	:param text            : The text of interest
	:param wrap_width      : The width at which lines are wrapped
	'''
	# Get a list of the numbers of wrapped lines that have been accumulated by the end of each of the lines
	num_wrapped_lines_by_end: List[int] = _num_wrapped_lines_by_end( text, wrap_width=wrap_width )

	# Convert to wrapped-line index and add the offset
	new_index: int = _wrapped_line_index_of_id( wrapped_line_id, num_wrapped_lines_by_end=num_wrapped_lines_by_end ) + offset

	# To help narrow down the search for the full-line index, calculate the furthest the full-line index could now be
	# (which can't have involved a move greater than offset because every full line has at least one wrapped line)
	# and then clamp between 0 and the number of lines (inclusive; not len-1 because bisect might need to return the one-after-end value)
	furthest_possible_full_line_index = max( 0, min( len( num_wrapped_lines_by_end ), wrapped_line_id.line_index + offset ) )

	# Convert the result back to a WrappedLineId
	#
	# (min_full_line_index shrinks the search range; the min ensures the range is big enough
	#  for negative offsets; the max ensures the range doesn't try below 0)
	return _wrapped_line_id_of_index(
		_wrapped_line_index_of_id( wrapped_line_id, num_wrapped_lines_by_end=num_wrapped_lines_by_end ) + offset,
		num_wrapped_lines_by_end=num_wrapped_lines_by_end,
		min_full_line_index = min( wrapped_line_id.line_index, furthest_possible_full_line_index ),
		max_full_line_index = max( wrapped_line_id.line_index, furthest_possible_full_line_index ),
	)

@dataclasses.dataclass
class WrappedLineRange:
	'''
	Specify a particular part of a particular full line of text in terms of the index of the full line
	and the begin/(one-past) end indices of the post-wrapping lines to include
	'''

	# The index of the unwrapped line from which this range of wrapped lines come
	line_index: int = 0

	# The begin index within the wrapped lines arising from wrapping the line_index-th line
	wrapped_begin_offset: int = 0

	# The (one-past) end index within the wrapped lines arising from wrapping the line_index-th line
	wrapped_end_offset: int = 0


def text_of_wrapped_line_range( disp_text: DisplayText,
                                wrp_rng: WrappedLineRange,
                                *,
                                term: blessed.Terminal,
                                wrap_width: WrapWidth,
                                ):
	'''
	The part of the specified DisplayText specified by the specified WrappedLineRange
	(wrapped using the specified blessed.Terminal and WrapWidth)

	:param disp_text  : The text to grab from
	:param wrp_rng    : The part to grab
	:param term       : The blessed.Terminal to use to calculate the lengths
	:param wrap_width : The width at which lines are wrapped
	'''
	# If the whole line is required, then just return that
	if wrp_rng.wrapped_begin_offset == 0 and wrp_rng.wrapped_end_offset == num_wrapped_lines_of_length(disp_text.line_term_lengths[wrp_rng.line_index], wrap_width=wrap_width):
		return disp_text.lines[wrp_rng.line_index]
	return term_printable_substring(
		disp_text.lines[wrp_rng.line_index],
		wrap_width.width * wrp_rng.wrapped_begin_offset,
		min(
			wrap_width.width * wrp_rng.wrapped_end_offset,
			disp_text.line_term_lengths[wrp_rng.line_index],
		),
		term=term,
	)


def wrapped_line_ranges_between( begin_id: WrappedLineId,
                                 end_id: WrappedLineId,
                                 *,
                                 line_term_lengths: List[int],
                                 wrap_width: WrapWidth,
                                 ) -> Iterable[WrappedLineRange]:
	'''
	WrappedLineRange specs to cover the text between begin_id and end_id, given the
	specified line_term_lengths and WrapWidth

	:param begin_id          : The begin WrappedLineId of the region of interest
	:param end_id            : The (one-past-)end WrappedLineId of the region of interest
	:param line_term_lengths : The terminal display lengths of the lines
	:param wrap_width        : The width at which lines are wrapped
	'''
	# Exclude empty lines
	return filter(
		lambda x: x.wrapped_begin_offset < x.wrapped_end_offset,
		(
			# Calculate the part of the line required
			WrappedLineRange(
				line_index=full_line_idx,
				wrapped_begin_offset=begin_id.wrapped_line_offset if full_line_idx == begin_id.line_index else 0,
				wrapped_end_offset=(
					end_id.wrapped_line_offset
					if full_line_idx == end_id.line_index else
					num_wrapped_lines_of_length(
						line_term_lengths[full_line_idx], wrap_width=wrap_width)
				)
			) for full_line_idx in range( begin_id.line_index, end_id.line_index + 1 )
		)
	)


def wrapped_lines_region_of( disp_text: DisplayText,
                             *,
                             term: blessed.Terminal,
                             begin_id: WrappedLineId,
                             max_num_wrapped_lines: int,
                             wrap_width: WrapWidth,
                             ) -> str:
	'''
	Return the part of the text to be displayed, starting from the specified WrappedLineId and
	continuing for max_num_wrapped_lines (using the specified blessed.Terminal and WrapWidth)

	Requires begin_id to be valid given this wrapping

	:param disp_text             : The text from which the part should be grabbed
	:param term                  : The blessed.Terminal to use to calculate the lengths
	:param begin_id              : The ID of the wrapped line from which to start
	:param max_num_wrapped_lines : The maximum number of wrapped lines to grab
	:param wrap_width            : The width at which lines are wrapped
	'''
	# Find the ID of the first line after the end of the region, or WrappedLineId(num_lines, 0)
	end_id: WrappedLineId = add_wrapped_line_offset(
		begin_id,
		max_num_wrapped_lines,
		text=disp_text,
		wrap_width=wrap_width,
	)

	return "\n".join(
		text_of_wrapped_line_range(
			disp_text,
			wrp_rng,
			term=term,
			wrap_width=wrap_width,
		)
		for wrp_rng in wrapped_line_ranges_between(
			begin_id,
			end_id,
			line_term_lengths=disp_text.line_term_lengths,
			wrap_width=wrap_width,
		)
	)

