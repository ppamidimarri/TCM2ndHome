#!/usr/bin/env python3

# This script downloads files from "SOURCE_PATH" on a remote
# server with SERVER_CREDENTIALS and saves them to the
# "RAW_PATH" location.

# This script should be run on the same device where TeslaCamMerge
# is running. It just pulls clips from the second home for processing.

import os
import time
import subprocess
import TCMConstants

SOURCE_PATH = '/home/pi/Upload'
SERVER_CREDENTIALS = 'pi@mv.pamidimarri.com'
SCP_PATH = '/usr/bin/scp'
SSH_PATH = '/usr/bin/ssh'

logger = TCMConstants.get_logger()

def main():
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCMConstants.exit_gracefully(TCMConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for folder in TCMConstants.FOOTAGE_FOLDERS:
			for item in list_remote_files(folder):
				file = item.decode("UTF-8")
				logger.debug("Found remote file {0}".format(file))
				if get_remote_file(file, folder):
					logger.info("Downloaded {0}".format(file))
					remove_source_file(file, folder)

		time.sleep(TCMConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	retVal = True
	for folder in TCMConstants.FOOTAGE_FOLDERS:
		retVal = retVal and TCMConstants.check_permissions("{0}{1}/{2}".format(TCMConstants.FOOTAGE_PATH, folder, TCMConstants.RAW_FOLDER), True)
	return retVal

### Loop functions ###

def get_remote_file(file, folder):
	command = "{0} {1}:{2}/{3}/{4} {5}{3}/{6}".format(SCP_PATH, SERVER_CREDENTIALS,
		SOURCE_PATH, folder, file, TCMConstants.FOOTAGE_PATH, TCMConstants.RAW_FOLDER)
	logger.debug("Executing command: {0}".format(command))
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error("Error running scp command {0}, returncode: {3}, stdout: {1}, stderr: {2}".format(
			command, completed.stdout, completed.stderr, completed.returncode))
		return False
	else:
		return True

def remove_source_file(file, folder):
	command = "{0} {1} rm {2}/{3}/{4}".format(SSH_PATH, SERVER_CREDENTIALS, SOURCE_PATH, folder, file)
	logger.debug("Executing command: {0}".format(command))
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error("Error running ssh command {0}, returncode: {3}, stdout: {1}, stderr: {2}".format(
			command, completed.stdout, completed.stderr, completed.returncode))

def list_remote_files(folder):
	command = "{0} {1} ls {2}/{3}".format(SSH_PATH, SERVER_CREDENTIALS, SOURCE_PATH, folder)
	logger.debug("Executing command: {0}".format(command))
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error("Error running ssh command {0}, returncode: {3}, stdout: {1}, stderr: {2}".format(
			command, completed.stdout, completed.stderr, completed.returncode))
		return []
	else:
		return completed.stdout.split()

if __name__ == '__main__':
	main()
