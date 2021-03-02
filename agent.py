# import multiprocessing as mp
from communicator import Communicator
from time import time, sleep
from random import randint
import csv
import os
import sys

"""
    just a small class to store logging information
"""
class LogEntry():
    ENTRY_ORDER = ['sys_time', 'logical_time', 'action', 'to', 'fromname', 'queue_len']
    def __init__(self, sys_time, logical_time, action, to=None, fromname=None, queue_len=None):
        self.sys_time = sys_time
        self.logical_time = logical_time
        self.action = action
        self.to = to
        self.fromname = fromname
        self.queue_len = queue_len


""" """
class Agent():
    """ """
    def __init__(self, lifetime, machine_index, num_machines):
        self.lifetime = lifetime  # in seconds
        self.machine_index = machine_index
        # find indices for other agents, assuming they lie in a contiguous block starting at "port"
        self.other_machines = [idx for idx in range(num_machines) if not idx == self.machine_index]
        self.logical_clock = 0
        self.ticks_per_second = randint(1, 6)
        # self.incoming_message_queue = deque()

        self.communicator = Communicator(self.machine_index, num_machines)

        # create log file and write its column headers
        self.log_filename = f'logs/log{int(time())}machine{machine_index}.csv'
        self.create_log()

        # begin conducting business
        self.main_loop()

    """ """
    def create_log(self):
        os.makedirs('logs', exist_ok=True)
        with open(self.log_filename, mode='a') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=LogEntry.ENTRY_ORDER)
            writer.writeheader()

    """ """
    def update_clock(self, newtime=None):
        if newtime is None:
            self.logical_clock += 1
        else:
            if newtime < self.logical_clock:
                raise Exception("wee woo! time is bad!")
            self.logical_clock = newtime

    """ """
    def handle_incoming_message(self, new_message, queue_len):
        sender, other_machine_logical_time = new_message
        # fast-forward clock if other machine's time is ahead
        if other_machine_logical_time > self.logical_clock:
            self.update_clock(newtime=other_machine_logical_time)

        # increment time by 1, regardless of whether other machine's clock is ahead
        self.update_clock()

        # log activity
        self.log_activity(LogEntry(
            sys_time=time(),
            logical_time=self.logical_clock,
            action="receive",
            fromname=sender,
            queue_len=queue_len
        ))

    """ """
    def send_message(self, recipient):
        # call communicator to send message
        msg = (self.machine_index, self.logical_clock)  # (sender, local logical time)
        # Need to convert tuple of ints to string
        self.communicator.send_message(recipient, '@@@'.join(map(str, msg)))

        # log activity
        self.log_activity(LogEntry(
            sys_time=time(),
            logical_time=self.logical_clock,
            action="send",
            to=recipient
        ))

    """ """
    def internal_event(self):
        # log activity
        self.log_activity(LogEntry(
            sys_time=time(),
            logical_time=self.logical_clock,
            action="work"
        ))

    """ """
    def do_random_task(self):
        # increment clock (according to Lamport this should happen before an event)
        self.update_clock()

        task_ID = randint(1,10)
        if task_ID == 1:
            self.send_message(recipient=self.other_machines[0])
        elif task_ID == 2:
            self.send_message(recipient=self.other_machines[1])
        elif task_ID == 3:
            self.send_message(recipient=self.other_machines[0])
            self.send_message(recipient=self.other_machines[1])
        else:
            self.internal_event()

    """
    """
    def main_loop(self):
        # run for only the allotted time (lifetime)
        for _ in range(self.lifetime * self.ticks_per_second):
            new_message, queue_len = self.communicator.get_message()
            if new_message is None:  # no incoming messages
                self.do_random_task()
            else:
                # Convert string message back into tuple of ints
                new_message = list(map(int, new_message.split('@@@')))
                self.handle_incoming_message(new_message, queue_len)

            sleep(1/self.ticks_per_second)

    """
    """
    def log_activity(self, log_entry):
        # open log file in "append mode"
        with open(self.log_filename, mode='a') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=LogEntry.ENTRY_ORDER)
            # add a row to the log: the attributes of log_entry, in fieldnames order
            writer.writerow(log_entry.__dict__)

if __name__ == '__main__':
    lifetime = int(sys.argv[1])
    machine_index = int(sys.argv[2])
    num_machines = int(sys.argv[3])
    agent = Agent(lifetime, machine_index, num_machines)
