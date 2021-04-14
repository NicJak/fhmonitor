import argparse
import json
import logging
import os
import threading
import time

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
    if not os.path.exists(path):
        logging.warning(path + " does not exist")
        return []
    if not os.access(path, os.R_OK):
        logging.warning("no access to " + path)
        return []
    config_files = []
    for backup_directory in get_subdirectories(path):
        config_directory = get_configuration_directory(backup_directory)
        if config_directory is not None:
            for config_file in next(os.walk(config_directory))[2]:
                config_files.append(os.path.join(config_directory, config_file))
    if len(config_files) == 0:
        logging.warning("No backup found in " + path)
    return config_files


def main():
    args = get_args()
    config = get_config(args.config)

    threads = []
    for backup in config:
        base = backup['path']
        for backup_config_file in get_backup_config_files(base):
            logging.info("monitoring " + backup_config_file)
            thread = threading.Thread(target=call_on_change, args=(backup_config_file, backup['url']))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    if len(threads):
        logging.warning("No backups are being monitored")

    while True:
        time.sleep(1)


def get_config(path):
    with open(path) as f:
        config = json.load(f)
    return config


def get_args():
    parser = argparse.ArgumentParser('Monitor your Win8/10 FileHistory instances from a server')
    parser.add_argument(dest='config', help='the configuration file path in xml')
    args = parser.parse_args()
    logging.info("Arguments = " + str(args))
    return args


logging.getLogger().setLevel(logging.INFO)

main()
