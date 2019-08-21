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

# Logging settings for TimedRotatingFileHandler, refer to:
# https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
# for details about the three supported options. The default
# is to rotate once a day and keep ten days' worth of logs.
LOG_WHEN = 'd'
LOG_INTERVAL = 1
LOG_BACKUP_COUNT = 10

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

def get_logger(filename):
	logger = logging.getLogger(filename)
	logger.setLevel(LOG_LEVEL)
	fh = logging.handlers.TimedRotatingFileHandler(
		LOG_PATH + filename + LOG_EXTENSION,
		when=LOG_WHEN, interval=LOG_INTERVAL,
		backupCount=LOG_BACKUP_COUNT)
	fh.setLevel(LOG_LEVEL)
	formatter = logging.Formatter(LOG_FORMAT)
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	logger.info("Starting up")
	return logger

def exit_gracefully(signum, frame):
	top_frame = frame.f_back
	while top_frame:
		if top_frame.f_back:
			top_frame = top_frame.f_back
		else:
			break
	caller = inspect.getframeinfo(top_frame).filename
	name = caller.rsplit('/', 1)[1][:-3] # Remove path, remove ".py" at the end
	logging.getLogger(name).info("Received signal {0}, exiting".format(signum))
	exit(signum)
