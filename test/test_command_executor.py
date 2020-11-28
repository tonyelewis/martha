import datetime
import pytest
import time

from pathlib import Path
from typing import List, Any

from command_helper import BIG_SEQ_VALUE, bytes_of_seq_value
from cppbuild.command_executor import CommandExecutor, CommandJob, finish_all, all_are_finished
from cppbuild.command_result import CommandResult


class ExeResultStasher:
	'''
	Provide a CommandExecutor post-processing callback and stash all the data
	'''
	def __init__(self):
		'''
		Create a stash
		'''
		self._stash: List[CommandResult] = []

	def post_process_callback( self,
	                           *,
	                           result: CommandResult,
	                           executor: CommandExecutor,
	                           ):
		'''
		The callback for CommandExecutor
		'''
		self._stash.append(result)

	@property
	def stash(self):
		'''
		Readonly access to the stash
		'''
		return self._stash


def test_finish_all():
	NUM_JOBS = 6
	command_executor = CommandExecutor(num_parallel_jobs=3,)
	command_executor.extend_queue(
		[CommandJob(command=['sleep', '0.0001']) for x in range(NUM_JOBS)]
	)

	start_time = datetime.datetime.now()
	assert not all_are_finished(command_executor)

	finish_all(command_executor)

	assert all_are_finished(command_executor)
	assert datetime.datetime.now() - start_time > datetime.timedelta(microseconds=100)


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
	assert not all_are_finished( command_executor )
	finish_all( command_executor )
	assert all_are_finished( command_executor )

	# Check the stashed results look sensible
	assert [x.returncode for x in stasher.stash] == [0] * NUM_JOBS
	assert [x.stderr for x in stasher.stash] == [b''] * NUM_JOBS
	assert all(__name__ in x.stdout.decode() for x in stasher.stash)
	assert sorted([x.associated_data
                for x in stasher.stash]) == list(range(NUM_JOBS))


def test_command_with_lot_of_output_does_not_block():
	NUM_JOBS = 6
	stasher = ExeResultStasher()
	command_executor = CommandExecutor(
		num_parallel_jobs=3,
		callback=stasher.post_process_callback,
	)
	command_executor.extend_queue(
		[CommandJob(command=['seq', str(BIG_SEQ_VALUE)], ) for _ in range(NUM_JOBS)]
	)
	finish_all(command_executor)

	assert len(stasher.stash) == NUM_JOBS
	EXPECTED_OUTPUT = bytes_of_seq_value(BIG_SEQ_VALUE)
	assert all(x.stdout == EXPECTED_OUTPUT for x in stasher.stash)
