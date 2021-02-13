import dataclasses


@dataclasses.dataclass(frozen=True)
class WrapWidth:
	'''
	A text-wrapping width

	(basically an int constrained to be strictly positive)
	'''

	# The width
	width: int

	def __post_init__(self):
		if type(self.width) != int or self.width <= 0:
			raise ValueError( f'wrap width must be a strictly positive integer, not { self.width }' )
