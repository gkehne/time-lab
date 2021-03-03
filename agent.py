# import multiprocessing as mp
from communicator import Communicator
from time import time, sleep
import random
import csv
import os
import sys

"""
    This is just a small class to store logging information.
    It allows the info to be passed to the csv writer as a dict, and stores the
    order in which the info should be written to the log.
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


"""
    This is the main class for each of the nodes in the test distributed system.
    At instantiation it takes parameters which allow it to create a Communicator
    object, which handles sending and receiving messages from the other agents,
    as well as `randint_max,` which controls the likelihood that it sends a
    message when there is none to receive.

    The Agent begins by randomly choosing its clock speed and instantiating a
    Communicator and log file, and then enters the main loop of the program,
    where it communicates back and forth with the other agents, logging its
    actions, until the 'lifetime' of the experiment is up.
"""
class Agent():
    """ """
    def __init__(self, lifetime, machine_index, num_machines, seed, uuid, randint_max=10, ticks_per_second=None):
        random.seed(seed)
        self.lifetime = lifetime  # runtime for the program, in seconds
        self.machine_index = machine_index
        # find indices for other agents, assuming they lie in a contiguous block starting at "port"
        self.other_machines = [idx for idx in range(num_machines) if not idx == self.machine_index]
        self.logical_clock = 0
        self.ticks_per_second = random.randint(1, 6) if ticks_per_second is None else ticks_per_second
        # self.incoming_message_queue = deque()
        print('Starting machine %d with %d ticks per second, seed %d' % (machine_index, self.ticks_per_second, seed))

        self.communicator = Communicator(self.machine_index, uuid)

        # create log file and write its column headers
        self.log_filename = f'logs/log{int(time())}machine{machine_index}.csv'
        self.create_log(num_machines)

        # begin conducting business
        self.randint_max = randint_max
        self.main_loop()

    def create_log(self, num_machines):
        """
            This helper method generates a log .csv with a name which includes
            the system time. It writes some extra info about the experiment
            run at the beginning of the log file, as well as the column headers.
            The action logs will be appended as rows one-by-one to the end.
        """

        os.makedirs('logs', exist_ok=True)

        #  record extra info at the top of the log file
        extra_info = [f'num machines: {num_machines}', f'ticks per second: {self.ticks_per_second}', f'lifetime: {self.lifetime}']
        dummy_info_dict = {k:info for k, info in zip(LogEntry.ENTRY_ORDER, extra_info)}

        with open(self.log_filename, mode='a') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=LogEntry.ENTRY_ORDER)
            writer.writerow(dummy_info_dict)
            writer.writeheader()

    def update_clock(self, newtime=None):
        """
            This method is the interface for the Agent to change its logical clock.
            It can either increment by 1 or fast-forward to a passed value.
            The passed value should be ahead of the current time.
        """
        if newtime is None:
            self.logical_clock += 1
        else:
            if newtime < self.logical_clock:
                raise Exception("wee woo! time is bad!")
            self.logical_clock = newtime

    def handle_incoming_message(self, new_message, queue_len):
        """
            This method takes an incoming message and reading of the Agent's
            incoming message queue length (BEFORE the message was removed), and
                1) updates the logical clock if necessary
                2) increments logical time
                3) logs the activity
        """
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

    def send_message(self, recipient):
        """
            This method takes takes the command to send an outgoing message and
                1) packages the message info (sender and logical time)
                2) hands it off to the Agent's Communicator
                3) logs the send
            Note that logical time incrementing happens at the caller to this
            method, since some "ticks" call this method twice.
        """
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

    def internal_event(self):
        """
            This is the agent action which is neither sending nor receiving
            messages. It
                2) incrmements the logical clock
                2) logs the activity
        """
        # log activity
        self.log_activity(LogEntry(
            sys_time=time(),
            logical_time=self.logical_clock,
            action="work"
        ))

    def do_random_task(self):
        """
            This randomly decides which non-message-receiving action the agent
            will perform. It
                1) increments logical time
                2) decides which activity to perform
                3) calls a sub-method to perform that activity
            Note that activity logging is performed by the activity-specific methods.
        """
        # increment clock (according to Lamport this should happen before an event)
        self.update_clock()

        task_ID = random.randint(1, self.randint_max)
        if task_ID == 1:
            self.send_message(recipient=self.other_machines[0])
        elif task_ID == 2:
            self.send_message(recipient=self.other_machines[1])
        elif task_ID == 3:
            self.send_message(recipient=self.other_machines[0])
            self.send_message(recipient=self.other_machines[1])
        else:
            self.internal_event()

    def main_loop(self):
        """
            This loop coordinates the behavior of the agents for the duration of
            the experiment's run. The number of loop iterations performed is
            determined by the ticks per minute of the Agent together with the
            (system-time) specified lifetime of the experiment. In each loop it
                1) checks with the Communicator for incoming messages
                2) performs the receive message action if so
                3) otherwise, chooses randomly between sending and internal actions.
                4) waits the precise amount until it's time to do the next iteration
        """
        # run for only the allotted time (lifetime)
        for _ in range(self.lifetime * self.ticks_per_second):
            start_time = time()
            new_message, queue_len = self.communicator.get_message()
            if new_message is None:  # no incoming messages
                self.do_random_task()
            else:
                # Convert string message back into tuple of ints
                new_message = list(map(int, new_message.split('@@@')))
                self.handle_incoming_message(new_message, queue_len)

            # this accounts for the time already taken in test_communication
            # and other activities from the total time allotted for the loop iteration
            already_taken = time() - start_time
            sleep_time = max(1/self.ticks_per_second - already_taken, 0)
            sleep(sleep_time)

    def log_activity(self, log_entry):
        """
            This appends a line to the log .csv file. The caller passes in a
            LogEntry object which contains the necessary data to be logged, and
            this writes it to the next row of the log in the correct order.
        """
        # open log file in "append mode"
        with open(self.log_filename, mode='a') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=LogEntry.ENTRY_ORDER)
            # add a row to the log: the attributes of log_entry, in fieldnames order
            writer.writerow(log_entry.__dict__)

"""
    This is called by the bash script to initialize the Agent.
    The bash script sets some of the parameters here, the script caller specifies
    the others, and all are passed in as sys args.
"""
if __name__ == '__main__':
    lifetime = int(sys.argv[1])
    machine_index = int(sys.argv[2])
    num_machines = int(sys.argv[3])
    seed = int(sys.argv[4])
    uuid = int(sys.argv[5])
    randint_max = int(sys.argv[6])
    
    # Optional argument for setting the frequency
    if len(sys.argv) == 8:
        tps = int(sys.argv[7])
    else:
        tps = None

    agent = Agent(lifetime, machine_index, num_machines, seed, uuid, randint_max, tps)
