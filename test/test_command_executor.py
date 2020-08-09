import pytest
import time

from pathlib import Path
from typing import List, Any

from cppbuild.command_executor import CommandExecutor, CommandJob


class ExeResultStasher:
	'''
	Provide a CommandExecutor post-processing callback and stash all the data
	'''

	def __init__(self):
		'''
		Create a stash
		'''
		self._stash = []
	
	def post_process_callback( self,
	                           *,
	                           returncode: int,
	                           stdout: str,
	                           stderr: str,
	                           command: List[str],
	                           run_dir: Path,
	                           associated_data: Any,
	                           ):
		'''
		The callback for CommandExecutor
		'''
		self._stash.append({
			'returncode'      : returncode,
			'stdout'          : stdout,
			'stderr'          : stderr,
			'command'         : command,
			'run_dir'         : run_dir,
			'associated_data' : associated_data,
		})

	@property
	def stash(self):
		'''
		Readonly access to the stash
		'''
		return self._stash


def test_compdb_of_compdb_str():
	NUM_JOBS = 6
	stasher = ExeResultStasher()

	# Start a CommandExecutor running NUM_JOBS ls commands
	command_executor = CommandExecutor(
		num_parallel_jobs=3,
		callback=stasher.post_process_callback,
	)
	command_executor.extend_queue(
		[CommandJob(
			command=['ls', str(Path(__file__).resolve().parent)],
			run_dir=Path('/'),
			associated_data=x,
		) for x in range(NUM_JOBS)]
	)

	# Assert there are jobs at the start
	# Wait for all the jobs to finish
	# Assert there are no jobs at the end
	assert command_executor.num_running() + command_executor.num_in_queue() > 0
	while not command_executor.all_are_finished():
		time.sleep(0.0002)
		command_executor.update()
	assert command_executor.num_running() + command_executor.num_in_queue() == 0

	# Check the stashed results look sensible
	assert [x['returncode'] for x in stasher.stash] == [0] * NUM_JOBS
	assert [x['stderr'] for x in stasher.stash] == [b''] * NUM_JOBS
	assert all(__name__ in x['stdout'].decode() for x in stasher.stash)
	assert sorted([x['associated_data']
                for x in stasher.stash]) == list(range(NUM_JOBS))
