""" Basic Redis master-slave cluster smoke test module """

import sys
import string
import random
from datetime import datetime
from traceback import print_exc
from redis import ResponseError
from RedisServer import RedisMaster, NoKeyException

def randomWord(length):
    """ Generates a random string with a length of choice """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


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
            except (NoKeyException, ResponseError) as exc:
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
                except (NoKeyException, ResponseError) as exc:
                    self.__failure(
                        master=master,
                        slave=slave,
                        reason=exc.__str__()
                    )
                else:
                    self.__success(master=master, slave=slave)
