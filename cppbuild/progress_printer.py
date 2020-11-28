import os
import sys

from typing import List, Optional, TextIO

from cppbuild.command_executor import CommandExecutor, all_are_finished, num_remaining
from cppbuild.command_result import CommandResult
from cppbuild.shlex_join import shlex_join_shim

class ProgressPrinter:
	'''
	Print progress working through commands
	'''

	def __init__( self,
	              *,
	              file: TextIO = sys.stdout,
	              ):
		'''
		Ctor

		:param file: The output to which the progress should be printed (default sys.stdout)
		'''

		# The output file
		self._outfile: TextIO = file

		# The number of jobs that have been reported with a success exit code
		self._num_succeeded: int = 0

		# The number of jobs that have been reported with a failure exit code
		self._num_failed: int = 0

		# Whether it has been registered that all commands have been added
		self._all_commands_added: bool = False

		# If using stdout and it's connected to a tty, turn the cursor off and record that's done
		#
		# Don't use this, use curses
		self._cursor_was_turned_off = False
		if self._outfile == sys.stdout and self._outfile_is_a_tty():
			os.system('setterm -cursor off')
			self._cursor_was_turned_off = True

	def __del__(self):
		'''If the cursor was turned off turn it back on when this is destroyed'''
		if self._cursor_was_turned_off:
			os.system('setterm -cursor on')

	def _outfile_is_a_tty(self) -> bool:
		'''Whether the output is connected to a tty'''
		return self._outfile.isatty()

	def _print_progress( self,
	                     *,
	                     num_remaining_commands: int,
	                     silent_if_redirected: bool,
	                     ) -> None:
		'''
		Print progress so far

		:param num_remaining_commands : The number of commands that are known to be remaining
		:param silent_if_redirected   : Whether to silence this printing if from a tty
		'''
		if silent_if_redirected and not self._outfile_is_a_tty():
			return

		if self._outfile_is_a_tty():
			print( end='\r', file=self._outfile )
		num_comp_coms_str_width = len(
			str(sum((num_remaining_commands, self._num_succeeded, self._num_failed))))
		print(
			( u'      \u001b[32;1m' if self._outfile_is_a_tty() else '' )
			+ f'{self._num_succeeded:>{num_comp_coms_str_width}} '
			+ u'\u2713'
			+ ( u'\u001b[0m' if self._outfile_is_a_tty() else '' )
			+'      '
			+ ( u'\u001b[31;1m' if self._outfile_is_a_tty() else '' )
			+ f'{self._num_failed:>{num_comp_coms_str_width}} '
			+ u'\u2717'
			+ ( u'\u001b[0m' if self._outfile_is_a_tty() else '' ),
			end='',
			file=self._outfile,
		)
		adding_str = ' ' if self._all_commands_added else '+'
		print(
			(
				f'      {num_remaining_commands:>{num_comp_coms_str_width}}{adding_str}' + u'\u231B      '
				if num_remaining_commands > 0
				else '      ' + ( ' ' * num_comp_coms_str_width ) +  '        '
			),
			end='',
			file=self._outfile,
			flush=True,
		)
		if not self._outfile_is_a_tty():
			print(file=self._outfile)

	def record_command_result( self,
	                           *,
	                           result: CommandResult,
	                           num_remaining_commands: int,
	                           ) -> None:
		'''
		Record the result of a command having been executed

		:param result                 : The result of the command execution
		:param num_remaining_commands : The number of remaining commands
		'''
		if result.returncode == 0:
			self._num_succeeded = self._num_succeeded + 1
		else:
			self._num_failed = self._num_failed + 1

			if self._outfile_is_a_tty():
				print( end='\r', file=self._outfile )

			print(shlex_join_shim(result.command), file=self._outfile )
			if result.stderr is not None:
				print(result.stderr.decode(), file=self._outfile )
			print( file=self._outfile )

		self._print_progress(
			num_remaining_commands=num_remaining_commands,
			silent_if_redirected=False,
		)

		if self._all_commands_added and num_remaining_commands == 0:
			print( file=self._outfile )

	def update_num_remaining( self,
	                          *,
	                          num_remaining_commands: int,
	                          ) -> None:
		'''
		Update the number of remaining commands

		This updates the live display if using a tty or do nothing otherwise

		:param num_remaining_commands : The new number of remaining commands
		'''
		self._print_progress(
			num_remaining_commands=num_remaining_commands,
			silent_if_redirected=True
		)

	def register_all_commands_have_been_added(self) -> None:
		'''Register that all commands have been added
		(so num_remaining_commands should no longer increase)'''
		self._all_commands_added = True

	@property
	def num_succeeded(self):
		'''
		Readonly access to num_succeeded
		'''
		return self._num_succeeded

	@property
	def num_failed(self):
		'''
		Readonly access to num_failed
		'''
		return self._num_failed
