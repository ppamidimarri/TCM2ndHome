#!/usr/bin/env python3

import logging
import os
import subprocess
import shutil
import time
import re
import TCConstants

logger = TCConstants.get_logger()

def main():
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCConstants.exit_gracefully(TCConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for folder in TCConstants.FOOTAGE_FOLDERS:
			for root, dirs, files in os.walk("{0}{1}".format(TCConstants.SHARE_PATH, folder), topdown=False):
				for name in files:
					if file_has_proper_name(name):
						move_file(os.path.join(root, name), folder)
					else:
						logger.debug("File '{0}' has invalid name, skipping".format(name))

		time.sleep(TCConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	retVal = True
	for folder in TCConstants.FOOTAGE_FOLDERS:
		retVal = retVal and TCConstants.check_permissions("{0}{1}".format(TCConstants.SHARE_PATH, folder), True)
		retVal = retVal and TCConstants.check_permissions("{0}{1}".format(TCConstants.UPLOAD_PATH, folder), True)
	return retVal

### Loop functions ###

def move_file(file, folder):
	logger.info("Moving file {0} in {1}".format(file, folder))
	if TCConstants.check_file_for_read(file):
		try:
			shutil.move(file, "{0}{1}".format(TCConstants.UPLOAD_PATH, folder))
			logger.debug("Moved file {0} in {1}".format(file, folder))
		except:
			logger.error("Failed to move {0} in {1}".format(file, folder))
	else:
		logger.debug("File {0} in {1} still being written, skipping for now".format(file, folder))

def file_has_proper_name(file):
	if TCConstants.FILENAME_PATTERN.match(file):
		return True
	else:
		return False

if __name__ == '__main__':
	main()
