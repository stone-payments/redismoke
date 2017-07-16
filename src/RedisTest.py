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

    class RedisTestMsg(object):
        def __init__(self, testId, success, action, master, slave=None, reason=None):
            self.testId = testId
            self.success = success
            self.action = action
            self.master = master
            self.slave = slave
            self.reason = reason

        def _action(self):
            if self.slave is None:
                subject = "master \"{}\"".format(self.master.name)
            else:
                subject = "slave \"{}\" of master \"{}\"".format(self.slave.name, self.master.name)

            if self.action == 'w':
                return "writing to {}".format(subject)
            elif self.action == 'r':
                return "reading from {}".format(subject)
            else:
                return "Unknown"

        def _failure(self):
            """ Print a standardized test failure message """
            if self.reason is not None:
                return "FAILURE[{}]: {}. Reason: {}.".format(self.testId, self._action(), self.reason)
            else:
                return "FAILURE[{}]: {}. Stack trace: ".format(self.testId, self._action())
                ## TODO: Fix this
                print_exc()
            sys.stdout.flush()

        def _success(self, master, slave=None):
            """ Print a standardized test success message """
            return "SUCCESS[{}]: {}.".format(self.testId, self._action())
            sys.stdout.flush()

        def __str__(self):
            if self.success:
                return self._success()
            else:
                return self._failure()
