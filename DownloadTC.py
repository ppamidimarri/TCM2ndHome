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
SERVER_CREDENTIALS = 'pi@second.home.com'
SCP_PATH = '/usr/bin/scp'
SSH_PATH = '/usr/bin/ssh'

logger = TCMConstants.get_logger()

def main():
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCMConstants.exit_gracefully(TCMConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for item in list_remote_files():
			file = item.decode("UTF-8")
			logger.debug("Found remote file {0}".format(file))
			if get_remote_file(file):
				logger.info("Downloaded {0}".format(file))
				remove_source_file(file)

		time.sleep(TCMConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	return TCMConstants.check_permissions(
		TCMConstants.RAW_PATH, True)

### Loop functions ###

def get_remote_file(file):
	command = "{0} {1}:{2}/{3} {4}".format(SCP_PATH, SERVER_CREDENTIALS,
		SOURCE_PATH, file, TCMConstants.RAW_PATH)
	logger.debug("Executing command: {0}".format(command))
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error("Error running scp command {0}, returncode: {3}, stdout: {1}, stderr: {2}".format(
			command, completed.stdout, completed.stderr, completed.returncode))
		return False
	else:
		return True

def remove_source_file(file):
	command = "{0} {1} rm {2}/{3}".format(SSH_PATH, SERVER_CREDENTIALS, SOURCE_PATH, file)
	logger.debug("Executing command: {0}".format(command))
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error("Error running ssh command {0}, returncode: {3}, stdout: {1}, stderr: {2}".format(
			command, completed.stdout, completed.stderr, completed.returncode))

def list_remote_files():
	command = "{0} {1} ls {2}".format(SSH_PATH, SERVER_CREDENTIALS, SOURCE_PATH)
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
