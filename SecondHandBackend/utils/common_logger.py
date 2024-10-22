import logging

logger = logging.getLogger('django')

import os
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from filelock import FileLock


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自定义日志按照日期分割，解决多进程问题"""

    @property
    def dfn(self):
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                addend = 3600 if dstNow else -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, timeTuple))
        return dfn

    def shouldRollover(self, record):
        """判断是否应该执行日志滚动操作"""
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return True
        return False

    def doRollover(self):
        """执行滚动操作"""
        if self.stream:
            self.stream.close()
            self.stream = None

        lock_path = self.baseFilename + '.lock'
        with FileLock(lock_path):
            attempt = 0
            while attempt < 5:  # 最多重试 5 次
                try:
                    dfn = self.dfn
                    if not os.path.exists(dfn):
                        self.rotate(self.baseFilename, dfn)

                    if self.backupCount > 0:
                        for s in self.getFilesToDelete():
                            os.remove(s)

                    if not self.delay:
                        self.stream = self._open()

                    currentTime = int(time.time())
                    newRolloverAt = self.computeRollover(currentTime)
                    while newRolloverAt <= currentTime:
                        newRolloverAt += self.interval

                    if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
                        dstAtRollover = time.localtime(newRolloverAt)[-1]
                        dstNow = time.localtime(currentTime)[-1]
                        if dstNow != dstAtRollover:
                            addend = -3600 if not dstNow else 3600
                            newRolloverAt += addend

                    self.rolloverAt = newRolloverAt
                    return  # 成功则返回

                except OSError as e:
                    if e.errno == 32:  # 文件正在被使用
                        attempt += 1
                        time.sleep(1)  # 等待 1 秒再重试
                        continue
                    logging.error(f"Error during log rollover: {e}")
                    break

import concurrent.futures
import time

# 配置日志
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler('test.log'), logging.StreamHandler()]
# )


# 写入日志的函数
def log_message(message):
    logger.error(message)
    print(message)
    time.sleep(1)  # 模拟写入延迟


def main():
    messages = [f"Message {i}" for i in range(10)]  # 要写入的日志信息
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(log_message, messages)  # 并发写入日志


