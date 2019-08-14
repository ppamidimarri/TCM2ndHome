#!/usr/bin/env python3

import logging
import os
import subprocess
import shutil
import signal
import time
import re
import TCConstants

logger_name = 'TC2Stager'
logger = logging.getLogger(logger_name)
logger.setLevel(TCConstants.LOG_LEVEL)

def main():
	fh = logging.FileHandler(TCConstants.LOG_PATH + logger_name + TCConstants.LOG_EXTENSION)
	fh.setLevel(TCConstants.LOG_LEVEL)
	formatter = logging.Formatter(TCConstants.LOG_FORMAT)
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	logger.info("Starting up")

	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		exit_gracefully(TCConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for root, dirs, files in os.walk(TCConstants.SHARE_PATH, topdown=False):
			for name in files:
				if file_has_proper_name(name):
					move_file(os.path.join(root, name))
				else:
					logger.debug("File '{0}' has invalid name, skipping".format(name))

		time.sleep(TCConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	return TCConstants.check_permissions(
		TCConstants.SHARE_PATH, True, logger) and TCConstants.check_permissions(
		TCConstants.UPLOAD_PATH, True, logger)

def exit_gracefully(signum, frame):
	logger.info("Received signal number {0}, exiting.".format(signum))
	exit(signum)

### Loop functions ###

def move_file(file):
	logger.info("Moving file {0}".format(file))
	if TCConstants.check_file_for_read(file, logger):
		try:
			shutil.move(file, TCConstants.UPLOAD_PATH)
			logger.debug("Moved file {0}".format(file))
		except:
			logger.error("Failed to move {0}".format(file))
	else:
		logger.debug("File {0} still being written, skipping for now".format(file))

def file_has_proper_name(file):
	if TCConstants.FILENAME_PATTERN.match(file):
		return True
	else:
		return False

if __name__ == '__main__':
	main()
