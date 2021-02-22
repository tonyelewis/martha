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

READY_TO_RECEIVE_SIGNAL_MSG = 'ready to receive signal'
SOME_TIME = datetime.timedelta( seconds=1 )
ZERO_TIME = datetime.timedelta( seconds=0 )

def sleep_but_send_message_on_signals( *,
                                       sleep_durn: datetime.timedelta,
                                       signals_to_handle: Optional[List[signal.Signals]] = None,
                                       also_on_normal_exit: bool,
                                       sendback_mesg: Optional[str],
                                       conn,
                                       ):
	'''
	Set-up an execute_on_signals() context manager, with an action to send the specified message on
	the specified connection, and then sleep for some time whilst that context manager is active

	This is intended to be run in another process, for testing execute_on_signals()

	:param sleep_durn          : The amount of time to sleep for
	:param signals_to_handle   : The signals to handle with execute_on_signals(), or None for default
	:param also_on_normal_exit : Whether the execute_on_signals() (if being used) should also perform the action on exit
	:param sendback_mesg       : The data that execute_on_signals() should send, if appropriate
	:param conn                : The connection that execute_on_signals() should send the data through, if appropriate
	'''
	# Prevent filling the output with stderr guff if/when this stops due to a signal
	sys.stderr = io.StringIO()

	# Use an execute_on_signals() context manager (specifying 'signals' as signals_to_handle if that isn't None),
	# send a message to indicate readiness, and then sleep
	kwargs: Dict[str, Any] = { 'also_on_normal_exit' : also_on_normal_exit }
	if signals_to_handle is not None:
		kwargs['signals'] = signals_to_handle
	with execute_on_signals( lambda:conn.send( sendback_mesg ), **kwargs ):
		conn.send( READY_TO_RECEIVE_SIGNAL_MSG )
		time.sleep( sleep_durn / datetime.timedelta( seconds=1 ) )


def other_process_executes_action( also_on_normal_exit: bool,
                                   signal_to_send: Optional[int] = None,
                                   signals_to_handle: Optional[List[signal.Signals]] = None,
                                   ) -> bool:
	'''
	Whether a separate process using execute_on_signals() (configured as specified) performs the action
	if sent the specified signal

	:param also_on_normal_exit : Whether the execute_on_signals() should be instructed to also perform the action on exit
	:param signal_to_send      : [Optional] The signal to send (or default to None, meaning sending none)
	:param signals_to_handle   : The signals the other process should handle with execute_on_signals(), or None for default
	'''
	EXECUTED_ACTION_MSG = 'executed action'

	# Prepare a multiprocessing pipe, and kwargs for sleep_but_send_message_on_signals()
	conn_a, conn_b = multiprocessing.Pipe()
	process_kwargs = {
		'also_on_normal_exit' : also_on_normal_exit,
		'conn'                : conn_b,
		'sendback_mesg'       : EXECUTED_ACTION_MSG,
		'sleep_durn'          : ZERO_TIME if signal_to_send is None else SOME_TIME,
	}
	if signals_to_handle is not None:
		process_kwargs['signals_to_handle'] = signals_to_handle

	# Create a process to run sleep_but_send_message_on_signals, start it, and wait for it to indicate that it's ready
	# (to receive any signal)
	process_handle = multiprocessing.Process(
		target = sleep_but_send_message_on_signals,
		kwargs = process_kwargs,
	)
	process_handle.start()
	assert conn_a.recv() == READY_TO_RECEIVE_SIGNAL_MSG

	# If a signal is to be sent, do so
	if signal_to_send is not None:
		assert process_handle.pid is not None
		os.kill(process_handle.pid, signal_to_send)

	# Wait for the process to complete and determine whether it sent the requested data back
	process_handle.join()
	received = conn_a.recv() if conn_a.poll() else None
	assert received is None or received == EXECUTED_ACTION_MSG
	return received == EXECUTED_ACTION_MSG


@pytest.mark.parametrize('also_on_normal_exit', (True, False))
@pytest.mark.parametrize('signal_to_send', (signal.SIGTERM, signal.SIGINT, None))
@pytest.mark.parametrize('signals_to_handle', ([], None))
def test_execute_on_signals_situations(also_on_normal_exit, signal_to_send, signals_to_handle):
	assert other_process_executes_action(
		also_on_normal_exit=also_on_normal_exit,
		signal_to_send=signal_to_send,
		signals_to_handle=signals_to_handle
	) == (
		( signal_to_send and ( signals_to_handle is None or signal_to_send in signals_to_handle ) )
		or
		( not signal_to_send and also_on_normal_exit )
	)
