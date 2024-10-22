import time
import datetime
import threading


class IdWorker:
    """生成用户的唯一十位的唯一id"""

    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        :param datacenter_id:数据id
        :param worker_id:机器id
        :param sequence:序列码
        """
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits

        self.epoch = 1288834974657
        self.last_timestamp = -1

        self.lock = threading.Lock()

    def _gen_timestamp(self):
        return int(time.time() * 1000)

    def _til_next_millis(self, last_timestamp):
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def get_id(self):
        with self.lock:
            timestamp = self._gen_timestamp()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            id = ((timestamp - self.epoch) << self.timestamp_left_shift) | (
                    self.datacenter_id << self.datacenter_id_shift) | (
                         self.worker_id << self.worker_id_shift) | self.sequence
            return id


def generate_out_trade_no():
    """
    生成商家订单编号
    """
    # 获取当前日期
    date = datetime.datetime.now().strftime("%Y%m%d")

    # 产品代码, productpix的缩写
    seller_code = "PF"

    # 订单序号
    worker = IdWorker(1, 2, 0)

    # 订单编号
    out_order_no = f"{date}{seller_code}{worker.get_id()}"

    return out_order_no


if __name__ == '__main__':
    worker = IdWorker(1, 2, 0)
    print(worker.get_id())
    print(len(str(worker.get_id())))

    out_order_no = generate_out_trade_no()
    print(out_order_no)
