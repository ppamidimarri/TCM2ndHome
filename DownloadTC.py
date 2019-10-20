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
REMOTE_LOG_PATH = '/home/pi/log'
SERVER_CREDENTIALS = 'pi@mv.pamidimarri.com'
SCP_PATH = '/usr/bin/scp'
SSH_PATH = '/usr/bin/ssh'
RSYNC_PATH = '/usr/bin/rsync'
SYNC_LOGS = True
LOG_NAMES_TO_RSYNC = ['TC2Stager.log', 'RemoveOldSecond.log']

logger = TCMConstants.get_logger()

def main():
	if not have_required_permissions():
		logger.error("Missing some required permissions, exiting")
		TCMConstants.exit_gracefully(TCMConstants.SPECIAL_EXIT_CODE, None)

	while True:
		if TCMConstants.MULTI_CAR:
			for car in TCMConstants.CAR_LIST:
				download_footage(f"{car}/")
		else:
			download_footage("")

		if SYNC_LOGS:
			for file in LOG_NAMES_TO_RSYNC:
				rsync_log_file(file)

		time.sleep(TCMConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
	have_perms = True
	if TCMConstants.MULTI_CAR:
		for car in TCMConstants.CAR_LIST:
			have_perms = have_perms and check_folder_perms(f"{car}/")
	else:
		have_perms = have_perms and check_folder_perms("")
	return have_perms

def check_folder_perms(car_path):
	have_perms = True
	for folder in TCMConstants.FOOTAGE_FOLDERS:
		have_perms = have_perms and TCMConstants.check_permissions(f"{TCMConstants.FOOTAGE_PATH}{car_path}{folder}/{TCMConstants.RAW_FOLDER}", True)
	return have_perms

### Loop functions ###

def download_footage(car_path):
	for folder in TCMConstants.FOOTAGE_FOLDERS:
		for item in list_remote_files(f"{car_path}{folder}"):
			file = item.decode("UTF-8")
			logger.debug(f"Found remote file {file}")
			if get_remote_file(file, f"{car_path}{folder}"):
				logger.info(f"Downloaded {file} into {car_path}{folder}")
				remove_source_file(file, f"{car_path}{folder}")

def get_remote_file(file, folder):
	command = f"{SCP_PATH} {SERVER_CREDENTIALS}:{SOURCE_PATH}/{folder}/{file} {TCMConstants.FOOTAGE_PATH}{folder}/{TCMConstants.RAW_FOLDER}"
	logger.debug(f"Executing command: {command}")
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error(f"Error running scp command: {command}, returncode: {completed.returncode}, stdout: {completed.stdout}, stderr: {completed.stderr}")
		return False
	else:
		return True

def remove_source_file(file, folder):
	command = f"{SSH_PATH} {SERVER_CREDENTIALS} rm {SOURCE_PATH}/{folder}/{file}"
	logger.debug(f"Executing command: {command}")
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error(f"Error running ssh command: {command}, returncode: {completed.returncode}, stdout: {completed.stdout}, stderr: {completed.stderr}")

def list_remote_files(folder):
	command = f"{SSH_PATH} {SERVER_CREDENTIALS} ls {SOURCE_PATH}/{folder}"
	logger.debug(f"Executing command: {command}")
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error(f"Error running ssh command: {command}, returncode: {completed.returncode}, stdout: {completed.stdout}, stderr: {completed.stderr}")
		return []
	else:
		return completed.stdout.split()

def rsync_log_file(file):
	command = f"{RSYNC_PATH} -e ssh {SERVER_CREDENTIALS}:{REMOTE_LOG_PATH}/{file} {TCMConstants.LOG_PATH}{file}"
	logger.debug(f"Executing command: {command}")
	completed = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if completed.stderr or completed.returncode != 0:
		logger.error(f"Error running rsync command: {command}, returncode: {completed.returncode}, stdout: {completed.stdout}, stderr: {completed.stderr}")

if __name__ == '__main__':
	main()
