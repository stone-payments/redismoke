""" Implement the needed code to render Redismoke capable of interacting with Solarwinds """

from RedisTest import RedisTestMsg

class RedisTestMsgSolarwinds(RedisTestMsg):
    """ Implement a RedisTestMsg interface that Solarwinds is capable of reading """
    def _failure(self):
        """ Print a standardized test failure message """
        if self.reason:
            msg = ("Statistic.{}: {}\n"
                   "Message.{}: {}").format(
                       self.server.name,
                       '0',
                       self.server.name,
                       self.reason
                   )
        else:
            msg = "Statistic.{}: {}".format(self.server.name, '0')
        return msg

    def _success(self):
        """ Print a standardized test success message """
        return "Statistic.{}: {}".format(self.server.name, '1')

    def __str__(self):
        return self._success() if self.success else self._failure()
