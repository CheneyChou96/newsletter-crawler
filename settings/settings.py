TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',  # MySQL or Mariadb
            'credentials': {
                'host': '66.112.219.229',
                'port': '3306',
                'user': 'newsletter',
                'password': 'HYLrKJsNF3Z&afbR',
                'database': 'newsletter_crawler',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                "echo": True
            }
        },
    },
    'apps': {
        'models': {
            #这个models就是自己配置的models.py位置
            'models': ['db.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}
