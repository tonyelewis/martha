import pytest

from text.wrap_width import WrapWidth


def test_wrap_width_allows_valid_values():
	WrapWidth(1)
	WrapWidth(2)
	WrapWidth(3)


def test_wrap_width_rejects_invalid_values():
	with pytest.raises(ValueError):
		WrapWidth(0)
	with pytest.raises(ValueError):
		WrapWidth(-1)


def test_wrap_width_prevents_assigning_new_values():
	a = WrapWidth(3)
	with pytest.raises(Exception):
		# Check that assigning a new value is prevented
		# (which needs a comment to prevent mypy complaining that that's not allowed)
		a.width = 5 # type: ignore[misc]
