import dataclasses


@dataclasses.dataclass
class WrappedLineId:
	'''
	Identify one of the post-wrapping lines of wrapped piece of text
	'''

	# The index of the unwrapped line from which this wrapped line comes
	line_index: int = 0

	# The index within the wrapped lines arising from wrapping the line_index-th line
	wrapped_line_offset: int = 0


def decremented_wrapped_line_offset_copy(wrapped_line_id: WrappedLineId) -> WrappedLineId:
	'''
	A copy of the specified WrappedLineId with the wrapped_line_offset decremented
	(or left as zero if it's already zero)

	:param wrapped_line_id : The WrappedLineId to decrement
	'''
	return dataclasses.replace(
		wrapped_line_id,
		wrapped_line_offset=max(1, wrapped_line_id.wrapped_line_offset) - 1,
	)


def incremented_wrapped_line_offset_copy(wrapped_line_id: WrappedLineId) -> WrappedLineId:
	'''
	A copy of the specified WrappedLineId with the wrapped_line_offset incremented

	:param wrapped_line_id : The WrappedLineId to increment
	'''
	return dataclasses.replace(
		wrapped_line_id,
		wrapped_line_offset=wrapped_line_id.wrapped_line_offset + 1,
	)
