""" Implement the needed code to render Redismoke capable of interacting with Solarwinds """

from RedisTest import RedisTestMsg

SERVICE_DOWN = '0'
SERVICE_UP = '1'

class RedisTestMsgSolarwinds(RedisTestMsg):
    # pylint: disable=R0903
    """ Implement a RedisTestMsg interface that Solarwinds is capable of reading """
    def _failure(self):
        """ Print a standardized test failure message """
        if self.reason:
            msg = ("Statistic.{}: {}\n"
                   "Message.{}: {}").format(
                       self.server.name,
                       SERVICE_DOWN,
                       self.server.name,
                       self.reason
                   )
        else:
            msg = "Statistic.{}: {}".format(self.server.name, SERVICE_DOWN)
        return msg

    def _success(self):
        """ Print a standardized test success message """
        return "Statistic.{}: {}".format(self.server.name, SERVICE_UP)

    def __str__(self):
        return self._success() if self.success else self._failure()
