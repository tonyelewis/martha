import io

import pytest

from cppbuild.command_result import CommandResult
from cppbuild.progress_printer import ProgressPrinter

def test_progress_printer():
	outfile = io.StringIO()

	progress_printer = ProgressPrinter(file=outfile)
	progress_printer.record_command_result(result=CommandResult(),num_remaining_commands=2)
	progress_printer.register_all_commands_have_been_added
	progress_printer.record_command_result(result=CommandResult(),num_remaining_commands=1)
	progress_printer.record_command_result(result=CommandResult(),num_remaining_commands=0)

	assert outfile.getvalue() == (
		  b'1 \xe2\x9c\x93      0 \xe2\x9c\x97      2+\xe2\x8c\x9b      \n'
		+ b'2 \xe2\x9c\x93      0 \xe2\x9c\x97      1+\xe2\x8c\x9b      \n'
		+ b'3 \xe2\x9c\x93      0 \xe2\x9c\x97               \n'
	).decode()
