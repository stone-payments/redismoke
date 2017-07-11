""" Basic Redis master-slave cluster smoke test """

import sys
import string
import random
from datetime import datetime
from traceback import print_exc
from time import sleep
import yaml
import redis

def randomWord(length):
    """ Generates a random string with a length of choice """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class NoKeyException(Exception):
    """ Exception raised when the RedisServer key doesn't exists """
    def __init__(self, key):
        Exception.__init__(self)
        self.key = key
    def __str__(self):
        return "Key " + self.key + " not found."

class RedisServer(object):
    """ Generic Redis Server object """
    def __init__(self, conf):
        self.name = conf['name'] if 'name' in conf and conf['name'] != "" else "Unammed"
        self.address = conf['address']
        self.port = conf['port'] if 'port' in conf and conf['port'] != "" else 6379
        self.password = conf['pass'] if 'pass' in conf else ""
        self.conn = None

    def disconnect(self):
        """ Close the connection to the RedisServer """
        del self.conn

    def connect(self):
        """ Open the connection with the RedisServer """
        if self.password == "":
            self.conn = redis.StrictRedis(
                host=self.address,
                port=self.port,
                db=0
            )
        else:
            self.conn = redis.StrictRedis(
                host=self.address,
                port=self.port,
                password=self.password,
                db=0
            )

    def read(self, key):
        """ Read a Redis key a return a string with the value """
        if self.conn is None:
            self.connect()
        value = self.conn.get(key)
        if value is None:
            raise NoKeyException(key)
        else:
            return bytes.decode(value)

    def write(self, key, value):
        """ Write a value to a key with TTL of 30s """
        if self.conn is None:
            self.connect()
        self.conn.setex(
            name=key,
            value=value,
            time=30
        )

    def __del__(self):
        self.disconnect()

class RedisMaster(RedisServer):
    """ A Redis Server that also hold slaves """
    def __init__(self, masterConf):
        RedisServer.__init__(self, masterConf)
        self.slaves = [RedisServer(slave) for slave in masterConf['slaves']]

class RedisTest(object):
    """ A test instance with multiple masters and their respectives slaves """
    def __init__(self, conf):
        self.testId = 'testid-' + randomWord(8)
        self.now = datetime.now().strftime("%Y%m%d%H%M%S.%N")
        self.masters = [RedisMaster(master) for master in conf['masters']]

    def __failure(self, master, slave=None, reason=None):
        """ Print a standardized test failure message """
        if slave is None:
            action = "writing to master \"" + master.name + "\""
        else:
            action = "reading from slave \"" + slave.name + "\" of master \"" + master.name + "\""
        if reason is not None:
            print("FAILURE[" + self.testId + "]: " + action + ". Reason: " + reason)
        else:
            print("FAILURE[" + self.testId + "]: "  + action + ". Stack trace: ")
            print_exc()
        sys.stdout.flush()

    def __success(self, master, slave=None):
        """ Print a standardized test success message """
        if slave is None:
            action = "writing to master \"" + master.name + "\"."
        else:
            action = "reading from slave \"" + slave.name + "\" of master \"" + master.name + "\"."
        print("SUCCESS[" + self.testId + "]: " + action)
        sys.stdout.flush()


    def write(self):
        """ Write in master a test key to be checked later """
        for master in self.masters:
            master.write(key=self.testId, value=self.now)

    def check(self):
        """ Verify that both masters and slaves have the test key """
        for master in self.masters:
            try:
                value = master.read(key=self.testId)
                if value != self.now:
                    self.__failure(
                        master=master,
                        reason="Wrong value."
                    )
            except (NoKeyException, redis.exceptions.ResponseError) as exc:
                self.__failure(
                    master=master,
                    reason=exc.__str__()
                )
            else:
                self.__success(master=master)
            for slave in master.slaves:
                try:
                    value = slave.read(key=self.testId)
                    if value != self.now:
                        self.__failure(
                            master=master,
                            slave=slave,
                            reason="Key " + self.testId + " has wrong value."
                        )
                except (NoKeyException, redis.exceptions.ResponseError) as exc:
                    self.__failure(
                        master=master,
                        slave=slave,
                        reason=exc.__str__()
                    )
                else:
                    self.__success(master=master, slave=slave)

with open(sys.argv[1], 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


while True:
    try:
        test = RedisTest(config)
        test.write()
        test.check()
        test = None
        sleep(config['pool'] if 'pool' in config and config['pool'] != "" else 60)
    except (KeyboardInterrupt, SystemExit):
        exit(0)
