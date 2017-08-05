""" Redismoke CLI """

from time import sleep
import argparse
import yaml
from RedisTestSolarwinds import RedisTestMsgSolarwinds
from RedisTest import RedisGroupTest

def main():
    parser = argparse.ArgumentParser(description="Test Redis replica sets")
    parser.add_argument(
        '--solarwinds',
        dest='solarwinds',
        action='store_true',
        help="Solarwinds-compatible output",
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

    if args.wait is not None:
        sleep(int(args.wait))

    if args.solarwinds is not None:
        try:
            test = RedisGroupTest(config, msgClass=RedisTestMsgSolarwinds)
            ok = test.run()
            exit(0 if ok else 3)
        except (KeyboardInterrupt, SystemExit):
            exit(2)
    else:
        while True:
            try:
                test = RedisGroupTest(config)
                test.run()
                test = None
                sleep(config['pool'] if 'pool' in config and config['pool'] != "" else 60)
            except (KeyboardInterrupt, SystemExit):
                exit(0)

if __name__ == "__main__":
    main()
