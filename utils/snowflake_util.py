import time


class Snowflake:
    def __init__(self, datacenter_id, worker_id):
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def generate_id(self):
        timestamp = self._get_current_timestamp()
        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp
        return (
                (timestamp << 22) |
                (self.datacenter_id << 17) |
                (self.worker_id << 12) |
                self.sequence
        )

    @staticmethod
    def _get_current_timestamp():
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._get_current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_current_timestamp()
        return timestamp


def get_snowflake_id():
    return Snowflake(datacenter_id=1, worker_id=1).generate_id()
