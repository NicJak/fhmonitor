import argparse
import json

parser = argparse.ArgumentParser('Monitor your Win8/10 FileHistory instances from a server')
parser.add_argument(dest='config', help='the configuration file path in xml')
args = parser.parse_args()

with open(args.config) as f:
  config = json.load(f)