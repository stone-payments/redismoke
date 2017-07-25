""" Redis abstraction layer for simple smoke test """

import redis

class NoKeyException(Exception):
    """ Exception raised when the RedisServer key doesn't exists """
    def __init__(self, key):
        Exception.__init__(self)
        self.key = key
    def __str__(self):
        return "Key " + self.key + " not found."

class RedisServer(object):
    """ Generic Redis Server object """
    # pylint: disable=R0902
    def __init__(self, conf, master=None):
        self.name = conf['name'] if 'name' in conf and conf['name'] != "" else "Unammed"
        self.address = conf['address']
        self.port = conf['port'] if 'port' in conf and conf['port'] != "" else 6379
        self.password = conf['pass'] if 'pass' in conf else ""
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
        super().__init__(masterConf)
        self.slaves = [RedisServer(slave) for slave in masterConf['slaves']]
