import json
import logging
import os

from dataclasses import dataclass
from pathlib import Path
from typing import List
from subprocess import PIPE, run

logger = logging.getLogger(__name__)


def _result_of_checked_ninja_run(command: List[str], **kwargs):
	'''
	Run the specified ninja command, raising a descriptive ChildProcessError if it fails or returning the
	run() result otherwise

	:param command : The command to execute
	:param kwargs  : Any other arguments to pass to run()
	'''
	command_result = run(command, stdout=PIPE, stderr=PIPE, **kwargs)
	if command_result.returncode != 0:
		raise ChildProcessError(
			f'Execution of ninja command "{ " ".join(command) }" failed with returncode {command_result.returncode}.'
			+ f' stdout was {command_result.stdout}.'
			+ f' stderr was { command_result.stderr }'
		)
	return command_result



def get_ninja_deps_str_for_dir(ninja_build_dir: Path) -> str:
	'''
	Call ninja to query the deps and return the resulting string

	:param ninja_build_dir: The ninja build directory to process
	'''

	logger.info( f'Calling ninja on directory {ninja_build_dir} to get deps...' )

	ninja_deps_result = _result_of_checked_ninja_run( [
		'ninja',
		'-C', str(ninja_build_dir),
		'-t', 'deps',
	] )

	return ninja_deps_result.stdout.decode()



@dataclass
class NinjaCompDBRecord:
	'''
	Represent one entry in a ninja compdb, using names matching those used by ninja

	This describes one command
	'''

	# The directory in which the command is run
	directory: Path

	# The command
	command: str

	# The primary input file
	file: Path

	# The name of the output target (may not be a file)
	output: str


def ninja_comp_db_record_of_raw_dict(x: dict):
	'''
	Make a NinjaCompDBRecord from the equivalent dict as parsed from `ninja -t compdb` json

	This is very similar to the from_dict() that gets provided by
	the @dataclass_json but that isn't used here because:

	 * this code should work without package dependencies
	 * this version converts two of the fields to Paths

	:param x: The dictionary from which to grab the data
	'''
	return NinjaCompDBRecord(
		directory = Path( x [ 'directory' ] ),
		command   =       x [ 'command'   ],
		file      = Path( x [ 'file'      ] ),
		output    =       x [ 'output'    ],
	)


def compdb_of_compdb_str(compdb_str: str) -> List[NinjaCompDBRecord]:
	'''
	Make a compdb (list of NinjaCompDBRecords) from the specified ninja compdb string

	:param compdb_str: A string as generated by `ninja compdb -t compdb`
	'''
	return [ninja_comp_db_record_of_raw_dict(x) for x in json.loads(compdb_str)]


def get_ninja_compdb_str_for_dir(ninja_build_dir: Path) -> List[NinjaCompDBRecord]:
	'''
	Call ninja to query the compdb and return the resulting string

	:param ninja_build_dir: The ninja build directory to process
	'''

	logger.info(
		f'Calling ninja on directory {ninja_build_dir} to get the compdb...'
	)

	ninja_compdb_result = _result_of_checked_ninja_run([
		'ninja',
		'-C', str(ninja_build_dir),
		'-t', 'compdb',
	])

	return ninja_compdb_result.stdout.decode()


def get_ninja_compdb_for_dir(ninja_build_dir: Path) -> List[NinjaCompDBRecord]:
	'''
	Call ninja to query the compdb and return the resulting compdb

	:param ninja_build_dir: The ninja build directory to process
	'''

	return compdb_of_compdb_str(get_ninja_compdb_str_for_dir(ninja_build_dir))


def project_dir_of_compdb(compdb: List[NinjaCompDBRecord]) -> Path:
	'''
	Extract the project directory from the specified compdb

	:param compdb: The compdb to search
	'''
	sought_output = 'build.ninja'
	sought_file_name = 'CMakeLists.txt'
	try:
		build_build_ninja_record = next(
			x
			for x
			in compdb
			if x.output == sought_output and x.file.name == sought_file_name
		)
	except StopIteration as e:
		raise ValueError( f'Cannot find any records in compdb with output {sought_output } and file name { sought_file_name }' )
	return Path( os.path.normpath( build_build_ninja_record.directory / build_build_ninja_record.file ) ).parent
