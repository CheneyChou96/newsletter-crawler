import redis

# 创建连接池
pool = redis.ConnectionPool(host='47.79.23.160', port=6379, password='ZCJV0DnuYq6VXeIz')

# 创建Redis实例，并设置decode_response为True
db = redis.Redis(connection_pool=pool)


def set_value(key, value):
    db.set(key, value)


def get_value(key):
    return db.get(key)


def del_value(key):
    db.delete(key)
    db.flushdb()


def flush_db():
    db.flushdb()


if __name__ == '__main__':
    set_value('test', '123456')
