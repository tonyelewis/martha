import dataclasses

from text.wrapped_line_id import WrappedLineId
from runner.execution_status import ExecutionStatus


@dataclasses.dataclass
class CommandTuiState:
	'''
	The TUI state of a command
	'''

	# The current status of command at present (RUNNING/SUCCEEDED/FAILED)
	status: ExecutionStatus

	# The index of the latest text from the command
	#
	# The execution_results should always have an entry in slot 0, so that can be the default
	text_index: int = 0

	# The position into the text to start display of it
	start_wli: WrappedLineId = WrappedLineId()
