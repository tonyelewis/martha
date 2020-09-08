import io
import subprocess
import threading

from dataclasses import dataclass
from typing import Callable


@dataclass
class DrainedByteStreams:
	'''
	Storage for the stderr/stdout bytes being drained in a SelfDrainingPopen
	'''

	# The stderr bytes
	stderr: bytes = b''

	# The stdout bytes
	stdout: bytes = b''

	def append_to_stderr(self, new_bytes: bytes) -> None:
		'''
		Append the specified bytes to the stderr bytes

		:param new_bytes: The bytes to append
		'''
		self.stderr += new_bytes

	def append_to_stdout(self, new_bytes: bytes) -> None:
		'''
		Append the specified bytes to the stderr bytes

		:param new_bytes: The bytes to append
		'''
		self.stdout += new_bytes


class SelfDrainingPopen:
	'''
	Do like Popen but use threading.Threads to drain the stdout/stderr streams
	'''

	def __init__(self, *args, **kwargs):
		'''
		Construct with arguments as for Popen(), except stderr/stdout may not be specified because
		this specifies them as subprocess.PIPE and then creates threads to drain them.
		'''
		if 'stderr' in kwargs or 'stdout' in kwargs:
			raise ValueError('stderr/stdout should not be specified to SelfDrainingPopen constructor')
		self._popen = subprocess.Popen(
				*args,
				**kwargs,
				stderr=subprocess.PIPE,
				stdout=subprocess.PIPE,
			)

		# Create DrainedByteStreams to which the Popen stderr/stdout can be drained
		self._drained_bytes = DrainedByteStreams()

		# Create a function to run in a thread to drain a stream
		def drain_output(buffer_stream: io.BufferedReader,
		                 append_bytes_fn: Callable[[DrainedByteStreams, bytes], None],
		                 ):
			read_bytes = buffer_stream.read()
			while len(read_bytes):
				append_bytes_fn( self._drained_bytes, read_bytes )
				read_bytes = buffer_stream.read()

		# Create a thread to drain each of ( stderr, stdout )
		self._drainer_threads: List[threading.Thread] = list(map(
			lambda x: threading.Thread(target=drain_output, args=x),
			(
				(self._popen.stderr, DrainedByteStreams.append_to_stderr),
				(self._popen.stdout, DrainedByteStreams.append_to_stdout),
			)
		))

		# Make the threads daemons and start them
		for drainer_thread in self._drainer_threads:
			drainer_thread.daemon = True
			drainer_thread.start()

	def poll(self):
		'''
		Like Popen.poll() but also require that draining threads are finished.

		Check if child process has terminated. Set and return returncode attribute. Otherwise, return None.
		'''
		poll_result = self._popen.poll()
		if poll_result is None:
			return None
		if any(x.is_alive() for x in self._drainer_threads):
			return None
		return poll_result

	@property
	def returncode(self):
		'''
		Readonly access to returncode
		'''
		return self._popen.returncode

	@property
	def stderr_bytes(self):
		'''
		Readonly access to stderr_bytes
		'''
		return self._drained_bytes.stderr

	@property
	def stdout_bytes(self):
		'''
		Readonly access to stdout_bytes
		'''
		return self._drained_bytes.stdout
