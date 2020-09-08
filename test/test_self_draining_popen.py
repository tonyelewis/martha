import pytest
import subprocess
import time

from cppbuild.self_draining_popen import SelfDrainingPopen
from command_helper import BIG_SEQ_VALUE, bytes_of_seq_value


def test_raises_on_attempt_to_specify_stderr_stdout_to_ctor():
	with pytest.raises(ValueError):
		sdo = SelfDrainingPopen(
			['seq', '2'],
			stderr=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL,
		)


def test_basic_command():
	sdo = SelfDrainingPopen(['seq', '5'])
	while sdo.poll() is None:
		time.sleep(0.0001)

	assert sdo.poll() == 0
	assert sdo.stderr_bytes == b''
	assert sdo.stdout_bytes == bytes_of_seq_value(5)


def test_command_with_lot_of_output_does_not_block():
	sdo = SelfDrainingPopen(['seq', str(BIG_SEQ_VALUE)])
	while sdo.poll() is None:
		time.sleep(0.0001)

	assert sdo.poll() == 0
	assert sdo.stderr_bytes == b''
	assert sdo.stdout_bytes == bytes_of_seq_value(BIG_SEQ_VALUE)


def test_stderr_output():
	sdo = SelfDrainingPopen(['ls', '/file/that/does/not/exist'])
	while sdo.poll() is None:
		time.sleep(0.0001)

	assert sdo.poll() != 0
	assert sdo.stderr_bytes == b"ls: cannot access '/file/that/does/not/exist': No such file or directory\n"
	assert sdo.stdout_bytes == b''
