import datetime
import io
import multiprocessing
import os
import pytest
import signal
import sys
import time

from typing import Any, Dict, List, Optional, Union

from process.execute_on_signals import execute_on_signals

LONG_TIME = datetime.timedelta( seconds=2 )
SHORT_TIME = datetime.timedelta( seconds=0.002 )

def other_process_function( *,
                            sleep_durn: datetime.timedelta,
                            handle_signals: Optional[Union[bool,List[signal.Signals]]] = None,
                            also_on_exit: bool,
                            sendback_data: Optional[str],
                            conn,
                            ):
	'''
	A function to run in another process and sleep for some time and optionally use a configured
    execute_on_signals() context manager to send some specified data on a specified connection.

	This can be used for testing the results of sending various signals, with and without execute_on_signals()

	:param sleep_durn     : The amount of time to sleep for
	:param handle_signals : The signals to handle with execute_on_signals(), or None for default, or False to not use execute_on_signals()
	:param also_on_exit   : Whether the execute_on_signals() (if being used) should also perform the action on exit
	:param sendback_data  : The data that execute_on_signals() should send, if appropriate
	:param conn           : The connection that execute_on_signals() should send the data through, if appropriate
	'''
	# Prevent filling the output with stderr guff if/when this stops due to a signal
	sys.stderr = io.StringIO()

	# If not handling signals, just sleep and return (without execute_on_signals())
	if handle_signals is not None and handle_signals == False:
		time.sleep( sleep_durn / datetime.timedelta( seconds=1 ) )
		return
	
	# Use a execute_on_signals() context manager
	# (specify signals as handle_signals if that isn't None)
	# and then sleep
	kwargs: Dict[str, Any] = { 'also_on_exit' : also_on_exit }
	if handle_signals:
		kwargs['signals'] = handle_signals
	with execute_on_signals( lambda:conn.send( sendback_data ), **kwargs ):
		time.sleep( sleep_durn / datetime.timedelta( seconds=1 ) )


def other_process_executes_action( also_on_exit: bool,
                                   test_signal: Optional[int] = None,
                                   handle_signals: Optional[Union[bool,List[signal.Signals]]] = None,
                                   ) -> bool:
	'''
	Whether a separate process using execute_on_signals() (as specified) performs the action
	if sent the specified signal

	:param also_on_exit   : Whether the execute_on_signals() should be instructed to also perform the action on exit
	:param test_signal    : [Optional] The signal to send (or default to None, meaning sending none)
	:param handle_signals : The signals the other process should handle with execute_on_signals(), or None for default, or False to not use execute_on_signals()
	'''

	# Prepare some data, a multiprocessing pipe, and kwargs for other_process_function()
	DATA = 'this is the data'
	conn_a, conn_b = multiprocessing.Pipe()
	process_kwargs = {
		'also_on_exit'  : also_on_exit,
		'conn'          : conn_b,
		'sendback_data' : DATA,
		'sleep_durn'    : SHORT_TIME if test_signal is None else LONG_TIME,
	}
	if handle_signals is not None:
		process_kwargs['handle_signals'] = handle_signals

	# Create a process to run other_process_function and start it
	process_handle = multiprocessing.Process(
		target = other_process_function,
		kwargs = process_kwargs,
	)
	process_handle.start()

	# If a signal is to be sent, give the process a short time to start up and then send the signal to it
	if test_signal is not None:
		time.sleep(SHORT_TIME / datetime.timedelta( seconds=1 ) )
		assert process_handle.pid is not None
		os.kill(process_handle.pid, test_signal)

	# Wait for the process to complete and determine whether it sent the requested data back
	process_handle.join()
	received = conn_a.recv() if conn_a.poll() else None
	assert received is None or received == DATA
	return received == DATA


@pytest.mark.parametrize('also_on_exit', (True, False))
@pytest.mark.parametrize('test_signal', (signal.SIGTERM, signal.SIGINT, None))
@pytest.mark.parametrize('handle_signals', (False, None))
def test_execute_on_signals_situations(also_on_exit, test_signal, handle_signals):
	assert other_process_executes_action(
		also_on_exit=also_on_exit,
		test_signal=test_signal,
		handle_signals=handle_signals
	) == (handle_signals is None and (test_signal is not None or also_on_exit))
