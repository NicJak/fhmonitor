import argparse
import json
import logging
import threading
import time

import requests
from inotify_simple import INotify, flags


def wait_for_change(path):
    inotify = INotify()
    try:
        inotify.add_watch(path, flags.CLOSE_WRITE)
        inotify.read()
        logging.info(path + " changed")
    except FileNotFoundError:
        logging.warning("File does not exist: " + path)
        time.sleep(60)


def call_on_change(path, url):
    while True:
        wait_for_change(path)
        requests.get(url)


parser = argparse.ArgumentParser('Monitor your Win8/10 FileHistory instances from a server')
parser.add_argument(dest='config', help='the configuration file path in xml')
args = parser.parse_args()

logging.info("Parameters = " + str(args))

with open(args.config) as f:
    config = json.load(f)

threads = []
for backup in config:
    thread = threading.Thread(target=call_on_change, args=(backup['path'], backup['url']))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
