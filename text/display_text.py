import blessed


class DisplayText:
	'''
	Text to be displayed on a terminal

	This caches the display-length of each line to speed up rendering different bits of it
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
			term.length( x ) for x in self._lines
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
