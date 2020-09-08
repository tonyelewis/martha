# This is big enough to cause seq's output to fill the standard Popen buffer
BIG_SEQ_VALUE = 99999


def bytes_of_seq_value(num: int) -> bytes:
	'''
	Generate the expected output of `seq <num>`, for testing purposes

	:param num : The argument to `seq`
	'''
	return (''.join(str(1 + x) + '\n' for x in range(num))).encode()
