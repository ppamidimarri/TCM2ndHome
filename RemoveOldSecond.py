#!/usr/bin/env python3

# This script removes:
# 	- empty directories within "SHARE_PATHS"
#	- video files under "VIDEO_PATHS"
# that have a name with a timestamp more than "DAYS_TO_KEEP" days old
# Files and directories who names don't match this format are left alone

import os
import time
import shutil
import logging
import TCConstants
import datetime
import re

VIDEO_PATHS = []

ALL_VIDEO_REGEX = f"{TCConstants.FILENAME_REGEX[:-5]}|fast|full).mp4"
ALL_VIDEO_PATTERN = re.compile(ALL_VIDEO_REGEX)

logger = TCConstants.get_logger()

def main():
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCConstants.exit_gracefully(TCConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for share in TCConstants.SHARE_PATHS:
			for folder in TCConstants.FOOTAGE_FOLDERS:
				for directory in next(os.walk(f"{share}{folder}"))[1]:
					if os.listdir(f"{share}{folder}/{directory}"):
						logger.debug(f"Directory {share}{folder}/{directory} not empty, skipping")
					else:
						remove_empty_old_directory(f"{share}{folder}/", directory)

		for path in VIDEO_PATHS:
			for file in os.listdir(path):
				remove_old_file(path, file)

		time.sleep(TCConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	have_perms = True
	for path in VIDEO_PATHS:
		have_perms = have_perms and TCConstants.check_permissions(path, True)
	for share in TCConstants.SHARE_PATHS:
		for folder in TCConstants.FOOTAGE_FOLDERS:
			have_perms = have_perms and TCConstants.check_permissions(f"{share}{folder}", True)
	return have_perms

### Loop functions ###

def remove_empty_old_directory(path, name):
	if is_old_enough(name):
		logger.info(f"Removing empty directory: {path}{name}")
		try:
			os.rmdir(f"{path}{name}")
		except:
			logger.error(f"Error removing directory: {path}{name}")
	else:
		logger.debug(f"Directory {path}{name} is not ready for deletion, skipping")

def remove_old_file(path, file):
	if is_old_enough(extract_stamp(file)):
		logger.info(f"Removing old file: {path}{file}")
		try:
			os.remove(f"{path}{file}")
			pass
		except:
			logger.error(f"Error removing file: {path}{file}")
	else:
		logger.debug(f"File {path}{file} is not ready for deletion, skipping")

def extract_stamp(file):
	match = ALL_VIDEO_PATTERN.match(file)
	if match:
		logger.debug(f"Returning stamp {match.group(1)[:-1]} for file {file}")
		return match.group(1)[:-1]
	else:
		logger.debug(f"No valid stamp found for file: {file}")
		return None

def is_old_enough(stamp_in_name):
	try:
		stamp = datetime.datetime.strptime(stamp_in_name, TCConstants.FILENAME_TIMESTAMP_FORMAT)
		age = datetime.datetime.now() - stamp
		if age.days > TCConstants.DAYS_TO_KEEP:
			return True
		else:
			return False
	except:
		logger.debug(f"Unrecognized name: {stamp_in_name}, skipping")
		return False

if __name__ == '__main__':
	main()
