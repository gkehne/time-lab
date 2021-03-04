import os
import csv
import pytest
from agent import Agent, LogEntry

'''
    This is a fake Communicator object used to test Agent
'''
class FakeCommunicator():
    def __init__(self):
        self.outbound_recipient = None
        self.outbound_message = None
        self.inbound_message = None, 0

    def send_message(self, recipient, msg):
        self.outbound_message = msg
        self.outbound_recipient = recipient

    def get_message(self):
        return self.inbound_message


# returns an agent object for other testing purposes
def make_test_agent():
    fake_communicator = FakeCommunicator()
    test_agent = Agent(
        lifetime=-1,  # ensures the main loop isn't entered
        machine_index=0,
        num_machines=3,
        seed=0,
        uuid=0,
        fake_test_communicator=fake_communicator
    )
    return test_agent

# deletes the test_agent's log file, if it exists
def cleanup(test_agent):
    try:
        os.remove(test_agent.log_filename)
    except FileNotFoundError:
        pass

# check initialized attributes that aren't just set directly from inputs
def test_agent_init():
    test_agent = make_test_agent()
    assert test_agent.other_machines == [1,2]
    assert test_agent.ticks_per_second in range(1,7)
    cleanup(test_agent)

# tests logging functionality of Agent
def test_logging():
    test_agent = make_test_agent()
    # it has already called create_log()
    with open(test_agent.log_filename, mode='r') as log_file:
        csv_reader = csv.reader(log_file)
        log_rows = list(csv_reader)
        assert log_rows[0] == ['num machines: 3', 'ticks per second: 4', 'lifetime: -1', '', '', '']
        assert log_rows[1] == ['sys_time', 'logical_time', 'action', 'to', 'fromname', 'queue_len']

    # call log_activity
    test_agent.log_activity(LogEntry(
        sys_time=10,
        logical_time=11,
        action="work"
    ))

    # enforce that the CSV test looks right
    with open(test_agent.log_filename, mode='r') as log_file:
        csv_reader = csv.reader(log_file)
        log_rows = list(csv_reader)
        assert log_rows[2] == ['10', '11', 'work', '', '', '']

    # delete test log
    cleanup(test_agent)

# tests clock update functionality
def test_logical_clock():
    test_agent = make_test_agent()
    test_agent.update_clock()
    assert test_agent.logical_clock == 1
    test_agent.update_clock(2)
    assert test_agent.logical_clock == 2
    cleanup(test_agent)

# tests communication capacity
def test_communication():
    test_agent = make_test_agent()
    test_agent.send_message(recipient=2)
    assert test_agent.communicator.outbound_recipient == 2
    assert test_agent.communicator.outbound_message == '0@@@0'  # machine index and current logical time
    cleanup(test_agent)
