""" Basic Redis master-slave cluster smoke test module """

import sys
import string
import random
from datetime import datetime
from redis import ResponseError
from RedisServer import RedisMaster, NoKeyException

IDLENGTH = 8

def _genRandomString(length):
    """ Generates a random string """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class RedisGroupTest(object):
    """ A group of test instances, each with its own Redis master """
    def __init__(self, conf):
        self.masters = [RedisMaster(master) for master in conf['masters']]
        self.tests = None

    def run(self):
        """ Instatiate and run each and every configured test """
        for master in self.masters:
            test = RedisTest(master)
            test.setup()
            test.check()

class RedisTest(object):
    """ A test instance with a single master and its respectives slaves """
    def __init__(self, master):
        self.testId = 'test-' + _genRandomString(IDLENGTH)
        self.now = datetime.now().strftime("%Y%m%d%H%M%S.%N")
        self.master = master
        for slave in master.slaves:
            slave.master = self.master

    def _replicasOk(self):
        replicasOk = True
        for slave in self.master.slaves:
            slaveOk = self._serverOk(slave)
            if not slaveOk:
                replicasOk = False
            print(RedisTestMsg(self.testId, action='r', server=slave))
            sys.stdout.flush()
        return replicasOk

    def _masterOk(self):
        masterOk = self._serverOk(self.master)
        print(RedisTestMsg(self.testId, action='r', server=self.master))
        sys.stdout.flush()
        return masterOk

    def _serverOk(self, server):
        """ Returns true if server has the test key correctly set, else false """
        try:
            value = server.read(key=self.testId)
            if value == self.now:
                server.setStatus(ok=True)
            else:
                server.setStatus(ok=False, reason="Invalid value")
        except (NoKeyException, ResponseError) as exc:
            server.setStatus(ok=False, reason=exc.__str__())
            return False
        return server.getStatus()[0]

    def setup(self):
        """ Write in master a test key to be checked later """
        self.master.write(key=self.testId, value=self.now)

    def check(self):
        """ Verify that both master and slaves have the test key """
        return self._masterOk() and self._replicasOk()

class RedisTestMsg(object):
    """ Informative message of the test result """
    def __init__(self, testId, action, server):
        self.testId = testId
        self.success = server.getStatus()[0]
        self.reason = server.getStatus()[1]
        self.action = action
        self.master = server.master if server.master != None else server
        self.slave = server if server.master != None else None

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
            return "FAILURE[{}]: {}. See stack trace.".format(self.testId, self._action())
        sys.stdout.flush()

    def _success(self):
        """ Print a standardized test success message """
        return "SUCCESS[{}]: {}.".format(self.testId, self._action())

    def __str__(self):
        if self.success:
            return self._success()
        else:
            return self._failure()
