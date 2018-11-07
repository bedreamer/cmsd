# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import select


class Selector(object):
    # 可读事件
    EVREADABLE = 1
    # 可写事件
    EVWRITABLE = 2

    def __init__(self):
        self.wait_readable_target_list = list()
        self.wait_writable_target_list = list()

    def run_forever(self):
        while True:
            self.run_step_forward()

    def run_step_forward(self):
        all_target_set = set(self.wait_readable_target_list + self.wait_writable_target_list)
        for target in all_target_set:
            target.setup(self)

        readable_prober_list = [target.file() for target in self.wait_readable_target_list]
        writable_prober_list = [target.file() for target in self.wait_writable_target_list]
        readable_list, writable_list, _ = select.select(readable_prober_list, writable_prober_list, [], 60)
        for target in all_target_set:
            file = target.file()

            if file in readable_list:
                target.on_readable()

            if file in writable_list:
                target.on_writable()

    def register(self, target, evt):
        if evt == Selector.EVREADABLE and target not in self.wait_readable_target_list:
            self.wait_readable_target_list.append(target)
        elif evt == Selector.EVWRITABLE and target not in self.wait_writable_target_list:
            self.wait_writable_target_list.append(target)
        else:
            pass

    def unregister(self, target, evt):
        if evt == Selector.EVREADABLE and target in self.wait_readable_target_list:
            self.wait_readable_target_list.remove(target)
        elif evt == Selector.EVWRITABLE and target in self.wait_writable_target_list:
            self.wait_writable_target_list.remove(target)
        else:
            pass
