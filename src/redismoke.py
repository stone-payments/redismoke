import sys
import string
import random
import datetime
import yaml
import redis

def randomWord(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class redisTest(object):
    def __init__(self, master):
        self.testId = 'testid-' + randomWord(8)
        self.now = datetime.datetime.now().strftime("%Y%m%d%H%M%S.%N")
        self.masterAddr = master['address']
        self.masterPort = master['port']
        self.password = master['pass']
        self.slaves = master['slaves']

    def writeMaster(self):
        try:
            masterConn = redis.StrictRedis(
                host=self.masterAddr,
                port=self.masterPort,
                password=self.password,
                db=0
            )
            masterConn.setex(
                name=self.testId,
                value=self.now,
                time=30
            )
        except exc:
            print(exc)
        finally:
            masterConn = None

    def checkSlave(self, name, address, port):
        try:
            slaveConn = redis.StrictRedis(
                host=address,
                port=port,
                password=self.password,
                db=0
            )
            readValue = bytes.decode(slaveConn.get(self.testId))
            if readValue != self.now:
                raise Exception("Slave " + name + " tá cagado.")
        except exc:
            print(exc)
        finally:
            slaveConn = None

    def checkSlaves(self):
        for slave in self.slaves:
            self.checkSlave(
                slave['name'],
                slave['address'],
                slave['port']
            )

with open(sys.argv[1], 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

for target in config['masters']:
    test = redisTest(target)
    test.writeMaster()
    test.checkSlaves()
