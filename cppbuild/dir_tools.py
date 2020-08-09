import os

from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkingDirChange:
	'''
	Represent a change of working directory (in which a command is executed)
	'''

	# The working directory in which some command was originally intended to be run
	prev_working_dir: Path

	# The new working directory in which we wish to run the command
	new_working_dir: Path

	def __post_init__(self):
		if self.prev_working_dir.is_absolute() != self.new_working_dir.is_absolute():
			raise ValueError(
				f'WorkingDirChange paths must both be absolute or both relative (prev_working_dir: { self.prev_working_dir }, new_working_dir: { self.new_working_dir })')


def from_changed_working_dir(path: Path,
                             working_dir_change: WorkingDirChange,
                             ) -> Path:
	'''
	Return a path modified according to a change in the working dir from which the path is seen

	:param path               : The input path
	:param working_dir_change : The change in working directory
	'''
	if path.is_absolute():
		return path

	return Path(
		os.path.normpath(str(working_dir_change.prev_working_dir / path))
	).relative_to(working_dir_change.new_working_dir)
