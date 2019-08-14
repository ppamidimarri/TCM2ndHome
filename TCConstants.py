import logging
import os
import subprocess
import re

# Location of CIFS share. MUST include trailing /. PROJECT_USER must have read-write permissions.
SHARE_PATH = '/samba/fjnuser/'

# Location for uploading
UPLOAD_PATH = '/home/pi/Upload/'

# Number of days to keep videos: applies to raw, full and fast videos.
# Videos that are older than these and in the FULL_PATH, FAST_PATH and
# RAW_PATH locations are automatically deleted by removeOld.service
# To keep videos longer, move them to any other directory, or move to
# the UPLOAD_PATH so they are automatically backed up to cloud storage.
DAYS_TO_KEEP = 30

# Settings for application logs
LOG_PATH = '/home/pi/log/'	# Must include trailing /, PROJECT_USER needs read-write permissions
LOG_EXTENSION = '.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# Paths of installed software, including name of the application
LSOF_PATH = '/usr/bin/lsof -t'							# Verify with: which lsof

### Do not modify anything below this line ###

# Characteristics of filenames output by TeslaCam
FILENAME_TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'
FILENAME_REGEX  = '(\d{4}(-\d\d){2}_(\d\d-){3})(right_repeater|front|left_repeater).mp4'
FILENAME_PATTERN = re.compile(FILENAME_REGEX)

# Application management constants
SLEEP_DURATION = 60
SPECIAL_EXIT_CODE = 115

# Common functions

def check_permissions(path, test_write, logger):
	if os.access(path, os.F_OK):
		logger.debug("Path {0} exists".format(path))
		if os.access(path, os.R_OK):
			logger.debug("Can read at path {0}".format(path))
			if test_write:
				if os.access(path, os.W_OK):
					logger.debug("Can write to path {0}".format(path))
					return True
				else:
					logger.error("Cannot write to path {0}".format(path))
					return False
			else:
				return True
		else:
			logger.error("Cannot read at path {0}".format(path))
			return False
	else:
		logger.error("Path {0} does not exist".format(path))
		return False

def check_file_for_read(file, logger):
	if os.access(file, os.F_OK):
		return not file_being_written(file, logger)
	else:
		logger.debug("File {0} does not exist".format(file))
		return False

def file_being_written(file, logger):
	completed = subprocess.run("{0} {1}".format(LSOF_PATH, file), shell=True,
		stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr:
		logger.error("Error running lsof on file {0}, stdout: {1}, stderr: {2}".format(
			file, completed.stdout, completed.stderr))
		return True # abundance of caution: if lsof won't run properly, postpone the merge!
	else:
		if completed.stdout:
			logger.debug("File {0} in use, stdout: {1}, stderr: {2}".format(
				file, completed.stdout, completed.stderr))
			return True
		else:
			return False

def check_file_for_write(file, logger):
	if os.access(file, os.F_OK):
		logger.debug("File {0} exists".format(file))
		return False
	else:
		return True
