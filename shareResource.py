import threading


class SharedResource:
    def __init__(self):
        self.flag = False
        self.variable = None
        self.condition = threading.Condition()

    def set_variable(self, new_value):
        with self.condition:
            self.variable = new_value
            self.flag = True
            # 通知等待的线程，条件已经满足
            self.condition.notify()

    def get_variable(self):
        with self.condition:
            # 等待条件满足
            while self.flag is False:
                self.condition.wait()
            self.flag = False
            return self.variable