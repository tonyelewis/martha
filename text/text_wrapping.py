from text.display_text import DisplayText, index_of_last_line, last_wrapped_line_num_of_line
from text.wrap_width import WrapWidth
from text.wrapped_line_id import WrappedLineId, decremented_wrapped_line_offset_copy, incremented_wrapped_line_offset_copy


def last_wrapped_line_id_of_line_index(line_index: int,
                                       *,
                                       text: DisplayText,
                                       wrap_width: WrapWidth,
                                       ) -> WrappedLineId:
	'''
	The WrappedLineId of the last wrapped line when wrapping the specified line of
	the specified DisplayText with the specified wrap_width

	Raises IndexError if line_index is out of range

	:param line_index : The index of the line of the text of interest
	:param text       : The DisplayText to query
	:param wrap_width : The length at which the text is to be wrapped
	'''
	return WrappedLineId(
		line_index=line_index,
		wrapped_line_offset=last_wrapped_line_num_of_line(
			text,
			line_index=line_index,
			wrap_width=wrap_width,
		)
	)


def id_of_wrapped_line_before_line(line_index: int,
                                   *,
                                   text: DisplayText,
                                   wrap_width: WrapWidth,
                                   ) -> WrappedLineId:
	'''
	The WrappedLineId of the last wrapped line when wrapping the line of
	the specified DisplayText before the specified one with the specified wrap_width

	If the line_index is 0, this returns (0,0)

	Raises IndexError if line_index is out of range

	:param line_index : The index of the line of the text after the one of interest
	:param text       : The DisplayText of interest
	:param wrap_width : The length at which the text is to be wrapped
	'''
	if line_index <= 0:
		return WrappedLineId(line_index=0, wrapped_line_offset=0)
	return last_wrapped_line_id_of_line_index(line_index - 1, text=text, wrap_width=wrap_width)


def constrained_to_text_and_width(wrapped_line_id: WrappedLineId,
                                  *,
                                  text: DisplayText,
                                  wrap_width: WrapWidth,
                                  ) -> WrappedLineId:
	'''
	Return a copy of the specified WrappedLineId that has been constrained to be valid
	in the specified DisplayText when wrapped with the specified wrap_width

	This should be done whenever the wrap_width may have changed since the WrappedLineId was calculated

	Raises IndexError if wrapped_line_id.line_index is out of range

	:param wrapped_line_id : The original WrappedLineId
	:param text            : The DisplayText of interest
	:param wrap_width      : The length at which the text is to be wrapped
	'''
	return WrappedLineId(
		line_index=wrapped_line_id.line_index,
		wrapped_line_offset=min(
			wrapped_line_id.wrapped_line_offset,
			last_wrapped_line_num_of_line(
				text,
				line_index=wrapped_line_id.line_index,
				wrap_width=wrap_width
			),
		),
	)


def id_of_wrapped_line_before_wrapped_line(wrapped_line_id: WrappedLineId,
                                           *,
                                           text: DisplayText,
                                           wrap_width: WrapWidth,
                                           ) -> WrappedLineId:
	'''
	The WrappedLineId of the wrapped line preceding the specified one in the specified text, with
	the specified wrap-width

	This should ensure the output is sensible, even if the input WrappedLineId isn't

	:param wrapped_line_id : The initial WrappedLineId
	:param text            : The DisplayText of interest
	:param wrap_width      : The width at which lines are wrapped
	'''
	constrained_wrapped_line_id = constrained_to_text_and_width(
		wrapped_line_id,
		text=text,
		wrap_width=wrap_width,
	)
	if constrained_wrapped_line_id.wrapped_line_offset > 0:
		return decremented_wrapped_line_offset_copy(constrained_wrapped_line_id)
	return id_of_wrapped_line_before_line(
		wrapped_line_id.line_index,
		text=text,
		wrap_width=wrap_width,
	)


def id_of_wrapped_line_after_wrapped_line(wrapped_line_id: WrappedLineId,
                                          *,
                                          text: DisplayText,
                                          wrap_width: WrapWidth,
                                          ) -> WrappedLineId:
	'''
	The WrappedLineId of the wrapped line following the specified one in the specified text, with
	the specified wrap-width

	This should ensure the output is sensible, even if the input WrappedLineId isn't

	:param wrapped_line_id : The initial WrappedLineId
	:param text            : The DisplayText of interest
	:param wrap_width      : The width at which lines are wrapped
	'''
	last_wrapped_line_num = last_wrapped_line_num_of_line(
		text,
		line_index=wrapped_line_id.line_index,
		wrap_width=wrap_width,
	)
	if wrapped_line_id.wrapped_line_offset < last_wrapped_line_num:
		return incremented_wrapped_line_offset_copy(wrapped_line_id)
	return WrappedLineId(
		line_index=min(index_of_last_line(text), wrapped_line_id.line_index + 1),
		wrapped_line_offset=0,
	)
