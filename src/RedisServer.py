""" Redis abstraction layer for simple smoke test """

import redis

DEFAULT_TTL = 30 #seconds
DEFAULT_DB = 0
DEFAULT_PORT = 6379
DEFAULT_TIMEOUT = 2.0

class NoKeyException(Exception):
    """ Exception raised when the key doesn't exists """
    def __init__(self, key):
        Exception.__init__(self)
        self.key = key
    def __str__(self):
        return "Key " + self.key + " not found."

class RedisServer(object):
    """ Generic Redis Server object """
    # pylint: disable=R0902
    def __init__(self, conf, master=None):
        self.name = conf.get('name', 'Unnamed')
        self.address = conf.get('address')
        self.port = conf.get('port', DEFAULT_PORT)
        self.password = conf.get('pass', "")
        self.conn = None
        self.ok = None
        self.reason = None
        self.master = master

    def setStatus(self, ok, reason=None):
        """ Set a server test outcome and reason """
        self.ok = ok
        self.reason = reason

    def getStatus(self):
        """ Return a boolean with the test outcome and the reason """
        return self.ok, self.reason

    def disconnect(self):
        """ Close the connection to the RedisServer """
        del self.conn

    def connect(self):
        """ Open the connection with the RedisServer """
        if self.password == "":
            self.conn = redis.StrictRedis(
                host=self.address,
                port=self.port,
                db=DEFAULT_DB,
                socket_timeout=DEFAULT_TIMEOUT
            )
        else:
            self.conn = redis.StrictRedis(
                host=self.address,
                port=self.port,
                password=self.password,
                db=DEFAULT_DB,
                socket_timeout=DEFAULT_TIMEOUT
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
        """ Write a value to a key that will auto-erase itself within DEFAULT_TTL seconds """
        if self.conn is None:
            self.connect()
        self.conn.setex(
            name=key,
            value=value,
            time=DEFAULT_TTL
        )

    def __del__(self):
        self.disconnect()

class RedisMaster(RedisServer):
    """ A Redis Server that also hold slaves """
    def __init__(self, masterConf):
        super().__init__(masterConf)
        self.slaves = [RedisServer(slave) for slave in masterConf['slaves']]
