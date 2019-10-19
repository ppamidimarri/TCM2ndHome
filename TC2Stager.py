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
	if len(TCMConstants.SHARE_PATHS) <= 0:
		logger.error("No share paths defined, please fix in TCConstants.py and restart.")
		TCConstants.exit_gracefully(TCConstants.SPECIAL_EXIT_CODE, None)
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCConstants.exit_gracefully(TCConstants.SPECIAL_EXIT_CODE, None)

	while True:
		for index, share in enumerate(TCConstants.SHARE_PATHS):
			for folder in TCConstants.FOOTAGE_FOLDERS:
				for root, dirs, files in os.walk(f"{share}{folder}", topdown=False):
					for name in files:
						if file_has_proper_name(name):
							sub_path = folder
							if TCConstants.MULTI_CAR:
								sub_path = f"{TCConstants.CAR_LIST[index]}{folder}"
							move_file(os.path.join(root, name), sub_path)
						else:
							logger.debug(f"File '{name}' has invalid name, skipping")

		time.sleep(TCConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	have_perms = True
	if TCConstants.MULTI_CAR:
		for car in TCConstants.CAR_LIST:
			have_perms = have_perms and check_folder_perms(f"{car}/")
	else:
		have_perms = have_perms and check_folder_perms("")
	return have_perms

def check_folder_perms(car_path):
	have_perms = True
	for folder in TCConstants.FOOTAGE_FOLDERS:
		for share in TCConstants.SHARE_PATHS:
			have_perms = have_perms and TCConstants.check_permissions("f{share}{folder}", True)
		have_perms = have_perms and TCConstants.check_permissions("f{TCConstants.UPLOAD_PATH}{car_path}{folder}", True)
	return have_perms

### Loop functions ###

def move_file(file, folder):
	logger.info(f"Moving file {file} in {folder}")
	if TCConstants.check_file_for_read(file):
		try:
			shutil.move(file, f"{TCConstants.UPLOAD_PATH}{folder}")
			logger.debug(f"Moved file {file} in {folder}")
		except:
			logger.error(f"Failed to move {file} in {folder}")
	else:
		logger.debug(f"File {file} in {folder} still being written, skipping for now")

def file_has_proper_name(file):
	if TCConstants.FILENAME_PATTERN.match(file):
		return True
	else:
		return False

if __name__ == '__main__':
	main()
