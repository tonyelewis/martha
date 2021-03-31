import enum


class ExecutionStatus(enum.Enum):
	'''
	The execution current state of a command
	'''
	RUNNING   = enum.auto() # The command is running
	SUCCEEDED = enum.auto() # The command has completed and succeeded
	FAILED    = enum.auto() # The command has completed and failed
