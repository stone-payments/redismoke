""" Basic Redis master-slave cluster smoke test module """

import sys
import string
import random
from datetime import datetime
from traceback import print_exc
from redis import ResponseError
from RedisServer import RedisMaster, NoKeyException

IDLENGTH = 8

def _genRandomString(length):
    """ Generates a random string """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class RedisTest(object):
    """ A test instance with multiple masters and their respectives slaves """
    def __init__(self, conf):
        self.testId = 'test-' + _genRandomString(IDLENGTH)
        self.now = datetime.now().strftime("%Y%m%d%H%M%S.%N")
        self.masters = [RedisMaster(master) for master in conf['masters']]

    def _failure(self, master, slave=None, reason=None):
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

    def _success(self, master, slave=None):
        """ Print a standardized test success message """
        if slave is None:
            action = "writing to master \"" + master.name + "\"."
        else:
            action = "reading from slave \"" + slave.name + "\" of master \"" + master.name + "\"."
        print("SUCCESS[" + self.testId + "]: " + action)
        sys.stdout.flush()

    def _serverOk(self, server):
        """ Returns true if server has the test key corretly set, else false """
        try:
            value = server.read(key=self.testId)
        except (NoKeyException, ResponseError) as exc:
            return False, exc.__str__()
        return value == self.now, None

    # pylint: disable=R1705
    def _groupOk(self, master):
        masterOk, masterReason = self._serverOk(master)
        groupOk = True
        if masterOk:
            self._success(master=master)
            groupOk = True
            for slave in master.slaves:
                slaveOk, slaveReason = self._serverOk(slave)
                if slaveOk:
                    self._success(master=master, slave=slave)
                else:
                    self._failure(master=master, slave=slave, reason=slaveReason)
                    groupOk = False
            return groupOk
        else:
            self._failure(master=master, reason=masterReason)
            return False

    def setup(self):
        """ Write in master a test key to be checked later """
        for master in self.masters:
            master.write(key=self.testId, value=self.now)

    def check(self):
        """ Verify that both masters and slaves have the test key """
        ok = True
        for master in self.masters:
            ok = self._groupOk(master) and ok
        return ok
