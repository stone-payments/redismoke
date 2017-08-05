""" Basic Redis master-slave cluster smoke test module """

import sys
import string
import random
from datetime import datetime
from redis import RedisError
from RedisServer import RedisMaster, NoKeyException

IDLENGTH = 8
TIMEFMT = "%Y%m%d%H%M%S.%N"
TESTPREFIX = "test-"

def _genRandomString(length):
    """ Generates a random string """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class RedisGroupTest(object):
    # pylint: disable=R0903
    """ A group of test instances, each with its own Redis master """
    def __init__(self, conf, msgClass=None):
        self.masters = [RedisMaster(master) for master in conf['masters']]
        self.tests = None
        self.msgClass = msgClass

    def run(self):
        """ Instatiate and run each and every configured test """
        runOk = True
        for master in self.masters:
            test = RedisTest(master, msgClass=self.msgClass)
            test.setup()
            runOk = test.check() and runOk
        return runOk

class RedisTest(object):
    """ A test instance with a single master and its respectives slaves """
    def __init__(self, master, msgClass=None):
        self.testId = TESTPREFIX + _genRandomString(IDLENGTH)
        self.now = datetime.now().strftime(TIMEFMT)
        self.master = master
        for slave in master.slaves:
            slave.master = self.master
        self.msgClass = RedisTestMsgOneline if msgClass is None else msgClass

    def _replicasOk(self):
        replicasOk = True
        for slave in self.master.slaves:
            slaveOk = self._serverOk(slave)
            if not slaveOk:
                replicasOk = False
            print(self.msgClass(self.testId, action='r', server=slave))
            sys.stdout.flush()
        return replicasOk

    def _masterOk(self):
        if self.master.getStatus()[0] is not False:
            masterOk = self._serverOk(self.master)
        else:
            masterOk = False
        print(self.msgClass(self.testId, action='r', server=self.master))
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
        except (NoKeyException, RedisError) as exc:
            server.setStatus(ok=False, reason=exc.__str__())
            return False
        return server.getStatus()[0]

    def setup(self):
        """ Write in master a test key to be checked later """
        try:
            self.master.write(key=self.testId, value=self.now)
        except RedisError as exc:
            self.master.setStatus(ok=False, reason=exc.__str__())
            return False
        return True

    def check(self):
        """ Verify that both master and slaves have the test key """
        return self._masterOk() and self._replicasOk()

class RedisTestMsg(object):
    # pylint: disable=R0903
    """ Abstract class of a Redis test result """
    def __init__(self, testId, action, server):
        self.testId = testId
        self.success = server.getStatus()[0]
        self.reason = server.getStatus()[1]
        self.action = action
        self.server = server
        self.master = server.master if server.master != None else server
        self.slave = server if server.master != None else None

    def _action(self):
        if self.slave is None:
            subject = "master \"{}\"".format(self.master.name)
        else:
            subject = "slave \"{}\" of master \"{}\"".format(self.slave.name, self.master.name)

        if self.action == 'w':
            action = "writing to {}".format(subject)
        elif self.action == 'r':
            action = "reading from {}".format(subject)
        else:
            action = "Unknown"
        return action

    def __str__(self):
        raise NotImplementedError

class RedisTestMsgOneline(RedisTestMsg):
    # pylint: disable=R0903
    """ Informative message of the test result """
    def _failure(self):
        """ Print a standardized test failure message """
        if self.reason:
            msg = "FAILURE[{}]: {}. Reason: {}.".format(self.testId, self._action(), self.reason)
        else:
            msg = "FAILURE[{}]: {}. See stack trace.".format(self.testId, self._action())
        return msg

    def _success(self):
        """ Print a standardized test success message """
        return "SUCCESS[{}]: {}.".format(self.testId, self._action())

    def __str__(self):
        return self._success() if self.success else self._failure()
