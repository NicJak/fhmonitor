import argparse
import json
import logging
import os
import threading
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileObserver(FileSystemEventHandler):
    def __init__(self, path, url):
        self.path = path
        self.url = url

    def on_modified(self, event):
        logging.info(self.path + " changed")
        requests.get(self.url)

    def on_closed(self, event):
        logging.info(self.path + " closed")
        requests.get(self.url)


def get_subdirectories(path):
    if not os.access(path, os.R_OK):
        logging.warning("no access to " + path)
        return []
    subdirectories = []
    for directory in next(os.walk(path))[1]:
        subdirectories.append(os.path.join(path, directory))
    return subdirectories


def get_configuration_directory(path):
    if not os.access(path, os.R_OK):
        logging.warning("no access to " + path)
        return None
    for directory in next(os.walk(path))[1]:
        if directory == 'Configuration':
            return os.path.join(path, directory)
    return None


def get_backup_config_directory(path):
    if not os.path.exists(path):
        logging.warning(path + " does not exist")
        return None
    if not os.access(path, os.R_OK):
        logging.warning("no access to " + path)
        return None
    for backup_directory in get_subdirectories(path):
        config_directory = get_configuration_directory(backup_directory)
        if config_directory is not None:
            return config_directory
    logging.warning("No backup found in " + path)
    return None


def to_observer(url, backup_config_directory):
    logging.info("monitoring " + str(backup_config_directory) + " under url " + url)
    observer = Observer()
    observer.schedule(FileObserver(backup_config_directory, url), backup_config_directory, recursive=True)
    observer.start()
    return observer


def get_config(path):
    with open(path) as f:
        config = json.load(f)
    return config


def main():
    args = get_args()
    config = get_config(args.config)

    observers = []
    for backup in config:
        directory = get_backup_config_directory(backup['path'])
        if directory is not None:
            observers.append(to_observer(backup['url'], directory))

    if len(observers) == 0:
        logging.warning("No backups are being monitored")

    try:
        while True:
            time.sleep(1)
    finally:
        for observer in observers:
            observer.stop()
            observer.join()


def get_args():
    parser = argparse.ArgumentParser('Monitor your Win8/10 FileHistory instances from a server')
    parser.add_argument(dest='config', help='the configuration file path in xml')
    args = parser.parse_args()
    logging.info("Arguments = " + str(args))
    return args


logging.getLogger().setLevel(logging.INFO)

main()
