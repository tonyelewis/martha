import contextlib
import signal

from typing import Any, Callable, Dict, List, Optional


@contextlib.contextmanager
def execute_on_signals(action: Callable,
                       *,
                       signals: Optional[List[signal.Signals]] = None, # pylint: disable=no-member
                       also_on_normal_exit: bool = False,
                       ):
	'''
	A context-manager that ensure the specified action is performed if/when any of the specified signals
	are being handled. This doesn't block the signal (it re-raises it).

	:param handle_signals      : (optional; default [ signal.SIGTERM, signal.SIGINT ]) The signals to handle
	:param also_on_normal_exit : Whether to also perform the action on normal exit
	'''
	signals_or_default = [ signal.SIGTERM, signal.SIGINT ] if signals is None else signals

	# Create a store of the handlers that were previously in place for each of the signals
	prev_handler_of_signal: Dict[int, Any] = { sig: None for sig in signals_or_default }

	def signal_handling_function(signum, _frame):
		# Reinstate the original signal handlers
		for sig in signals_or_default:
			signal.signal( sig, prev_handler_of_signal[ sig ] )

		# Perform the action
		action()

		# Re-raise the signal
		signal.raise_signal(signum)

	# Install the signal_handling_function for each of the signals,
	# recording each previous handler in prev_handler_of_signal
	for sig in signals_or_default:
		prev_handler_of_signal[ sig ] = signal.signal( sig, signal_handling_function )

	# Yield control back to the function using this context-manager
	yield

	# If the action is to be performed on normal exit, perform it
	if also_on_normal_exit:
		action()
