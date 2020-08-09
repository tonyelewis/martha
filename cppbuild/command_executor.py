from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Any, Callable, Iterable, List, Optional, Tuple


@dataclass
class CommandJob:
	'''
	Represent one command job to be performed 
	'''

	# The command to be performed
	command: List[str]

	# The directory in which the command should be performed
	run_dir: Path

	# Data associated with the command that will be passed in the post-completion callback
	associated_data: Any


def _do_nothing(*args, **kwargs):
	pass


class CommandExecutor:
	def __init__(self, *, num_parallel_jobs: int, callback: Callable = _do_nothing):
		'''
		Construct

		:param num_parallel_jobs : The maximum number of commands to execute simultaneously
		:param callback          : A callback to call once after job completes with the details
		'''

		# Stash the callback
		self.callback: Callable = callback

		# Create a list of slots in which to perform the jobs
		self._running_jobs: List[
			Optional[Tuple[Popen, CommandJob]]
		] = [None] * num_parallel_jobs

		# Create a queue of jobs that have not yet been started
		self._queue: List[CommandJob] = []


	# def terminate_all_and_wipe_queue();
	# 	# TODO: later, can add optional callback predicate determining whether a specific job should be wiped


	def update(self) -> None:
		'''
		Update all computation slots, processing any completed jobs and
		starting any queued jobs in any free slots
		'''

		# Loop over the running jobs
		for index, popen_slot in enumerate(self._running_jobs):

			# If this job is complete, grab it and free up the slot
			retrieved_job = None
			if popen_slot is not None:
				return_code_if_complete = popen_slot[0].poll()
				if return_code_if_complete is not None:
					retrieved_job = popen_slot
					self._running_jobs[index] = None

			# If this slot is free and there are jobs in the queue,
			# pop the first one off and start it running
			if self._running_jobs[index] is None:
				if len(self._queue):
					command_job = self._queue.pop(0)
					self._running_jobs[index] = (
						Popen(
							command_job.command,
							cwd=command_job.run_dir,
							stdout=PIPE,
							stderr=PIPE
						),
						command_job,
					)

			# If a completed job was grabbed, post-process it
			if retrieved_job is not None:
				completed_popen: Popen
				job_details: CommandJob
				completed_popen, job_details = retrieved_job
				self.callback(
					returncode=completed_popen.returncode,
					stdout='' if completed_popen.stdout is None else completed_popen.stdout.read(),
					stderr='' if completed_popen.stderr is None else completed_popen.stderr.read(),
					command=job_details.command,
					run_dir=job_details.run_dir,
					associated_data=job_details.associated_data,
				)

	def all_are_finished(self) -> bool:
		'''
		Extend the queue with the specified CommandJobs and update
		'''
		return (
			self.num_in_queue() == 0
			and
			all(x is None for x in self._running_jobs)
		)

	def extend_queue(self, jobs: Iterable[CommandJob]) -> None:
		'''
		Extend the queue with the specified CommandJobs and update

		:param jobs: The jobs to add
		'''
		self._queue.extend(jobs)
		self.update()

	def num_running(self) -> int:
		'''
		The number of jobs currently running
		(or complete but not processed as complete)

		This doesn't update jobs.
		'''
		return sum(1 if x is not None else 0 for x in self._running_jobs)

	def num_in_queue(self) -> int:
		'''
		The number of jobs waiting in the queue
		'''
		return len(self._queue)
