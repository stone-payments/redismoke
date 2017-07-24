""" Redismoke CLI """

import sys
from time import sleep
import yaml
from RedisTest import RedisGroupTest

with open(sys.argv[1], 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

while True:
    try:
        test = RedisGroupTest(config)
        test.run()
        test = None
        sleep(config['pool'] if 'pool' in config and config['pool'] != "" else 60)
    except (KeyboardInterrupt, SystemExit):
        exit(0)
