import redis


class RedisConn:
    def __init__(self, host=None, port=None, db=None, password=None):
        pool = redis.ConnectionPool(
            db=db,
            password=password,
            host=host,
            port=port,
            decode_responses=True
        )

        self.conn = redis.Redis(connection_pool=pool)

    def get_conn(self):
        return self.conn
