import argparse
import json
import logging
import os
import threading

import requests
from inotify_simple import INotify, flags


def wait_for_change(path):
    inotify = INotify()
    inotify.add_watch(path, flags.CLOSE_WRITE)
    inotify.read()
    logging.info(path + " changed")


def call_on_change(path, url):
    while True:
        wait_for_change(path)
        requests.get(url)


def get_subdirectories(path):
    subdirectories = []
    for directory in next(os.walk(path))[1]:
        subdirectories.append(os.path.join(path, directory))
    return subdirectories


def get_configuration_directory(path):
    for directory in next(os.walk(path))[1]:
        if directory == 'Configuration':
            return os.path.join(path, directory)
    return None


def get_backup_config_files(path):
    config_files = []
    for backup_directory in get_subdirectories(path):
        config_directory = get_configuration_directory(backup_directory)
        if config_directory is not None:
            for config_file in next(os.walk(config_directory))[2]:
                config_files.append(os.path.join(config_directory, config_file))
    return config_files


logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser('Monitor your Win8/10 FileHistory instances from a server')
parser.add_argument(dest='config', help='the configuration file path in xml')
args = parser.parse_args()

logging.info("Parameters = " + str(args))

with open(args.config) as f:
    config = json.load(f)

threads = []
for backup in config:
    base = backup['path']
    if not os.path.exists(base):
        logging.warning(base + " does not exist")
        continue
    backup_directory = get_backup_config_files(base)
    if len(backup_directory) == 0:
        logging.warning("No backup found in " + base)
    for file in backup_directory:
        logging.info("monitoring " + file)
        thread = threading.Thread(target=call_on_change, args=(file, backup['url']))
        threads.append(thread)
        thread.start()

for thread in threads:
    thread.join()
