import blessed  # type: ignore[import]

from typing import List

from text.wrap_width import WrapWidth

class DisplayText:
	'''
	Text to be displayed on a terminal, broken into lines

	This caches the display-length of each line to speed up rendering sub-regions of it

	This must always contain at least one line of an empty string
	'''

	def __init__( self,
	              text: str,
	              *,
	              term: blessed.Terminal
	              ):
		'''
		Ctor from the text and a terminal, used to calculate the display-length of each line

		:param text : The raw text to be displayed, which may contain terminal escape sequences
		:param term : The blessed.Terminal to use to calculate the lengths
		'''
		self._lines: List[str] = text.split("\n")
		self._line_term_lengths: List[int] = [
			term.length(x) for x in self._lines
		]

	@property
	def lines(self):
		'''
		Readonly access to the lines
		'''
		return self._lines

	@property
	def line_term_lengths(self):
		'''
		Readonly access to the line_term_lengths
		'''
		return self._line_term_lengths


def index_of_last_line(text: DisplayText) -> int:
	'''
	The index of the last line in the text

	:param text : The DisplayText to query
	'''
	return max(1, len(text.lines)) - 1


def num_wrapped_lines_of_length(length: int,
                                *,
                                wrap_width: WrapWidth,
                                ) -> int:
	'''
	The number of wrapped lines of text in the specified (display) length of text, given the specified wrap_width

	This will always return an answer ≥ 1, because even a string of length 0 has 1 wrapped line

	:param length     : The length of the line of text
	:param wrap_width : The length at which the text is wrapped
	'''
	return max( 1, -(-length // wrap_width.width))


def last_wrapped_line_num_of_length(length: int,
                                    *,
                                    wrap_width: WrapWidth,
                                    ) -> int:
	'''
	The index of the last wrapped line of text in the specified (display) length of text, given the specified wrap_width

	:param length     : The length of the line of text
	:param wrap_width : The length at which the text is wrapped
	'''
	# Subtraction is always OK because the result of num_wrapped_lines_of_length() is always ≥ 1
	return num_wrapped_lines_of_length(length, wrap_width=wrap_width) - 1


def num_wrapped_lines_of_line(text: DisplayText,
                              *,
                              line_index: int,
                              wrap_width: WrapWidth,
                              ) -> int:
	'''
	The number of wrapped lines of the line at the specified index in the specified DisplayText,
	given the specified wrap_width

	:param text       : The DisplayText to query
	:param line_index : The index of the line of text of interest
	:param wrap_width : The length at which the text is wrapped
	'''
	return num_wrapped_lines_of_length(text.line_term_lengths[line_index], wrap_width=wrap_width)


def last_wrapped_line_num_of_line(text: DisplayText,
                                  *,
                                  line_index: int,
                                  wrap_width: WrapWidth,
                                  ) -> int:
	'''
	The index of the last wrapped line of text arising from wrapping the line at the specified index in
	the specified DisplayText with the specified wrap_width (or 0 if the line is empty).

	:param text       : The DisplayText to query
	:param line_index : The index of the line of text of interest
	:param wrap_width : The length at which the text is wrapped
	'''
	return last_wrapped_line_num_of_length(text.line_term_lengths[line_index], wrap_width=wrap_width)
