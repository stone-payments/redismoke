import sys
from RedisTest import RedisTestMsg

class RedisTestMsgSolarwinds(RedisTestMsg):
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
