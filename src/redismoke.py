""" Redismoke CLI """

from time import sleep
import argparse
import yaml
from RedisTestSolarwinds import RedisTestMsgSolarwinds
from RedisTest import RedisGroupTest

# Those exit codes are documented in SolarWinds docs, in the following page:
# http://www.solarwinds.com/documentation/en/flarehelp/sam/content/sam-linux-unix-script-monitor-sw3260.htm
EXIT_OK = 0
EXIT_CRITICAL = 3
EXIT_ABORT = 4

def main():
    """ Parse the arguments, parse the config file and call the tests to run """
    parser = argparse.ArgumentParser(description="Test Redis replica sets")
    parser.add_argument(
        '--solarwinds',
        dest='solarwinds',
        action='store_true',
        help="Solarwinds-compatible output",
        default=False
        )
    parser.add_argument(
        '--config',
        dest='config',
        nargs='?',
        help="Config file",
        default='redismoke.yml')
    parser.add_argument(
        '--wait',
        dest='wait',
        nargs='?',
        help="Wait seconds before running",
        default=0)
    args = parser.parse_args()

    with open(args.config, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    sleep(int(args.wait))

    if args.solarwinds:
        try:
            test = RedisGroupTest(config, msgClass=RedisTestMsgSolarwinds)
            ok = test.run()
            exit(EXIT_OK if ok else EXIT_CRITICAL)
        except KeyboardInterrupt:
            exit(EXIT_ABORT)
    else:
        while True:
            try:
                test = RedisGroupTest(config)
                test.run()
                test = None
                sleep(config.get('pool', 60))
            except (KeyboardInterrupt, SystemExit):
                exit(EXIT_ABORT)

if __name__ == "__main__":
    main()
