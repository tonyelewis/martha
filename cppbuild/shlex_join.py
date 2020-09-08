import shlex

from typing import List


def shlex_join_shim(command_parts: List[str],
                    joinee: str = ' '
                    ) -> str:
	'''
	Shim slex.join(), which was only added in Python 3.8

	See https://docs.python.org/3/library/shlex.html#shlex.join

	:param command_parts : The command parts to join
	:param joinee        : The join string to use (default: ' ')
	'''
	return joinee.join(shlex.quote(part) for part in command_parts)
