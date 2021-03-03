import pytest
from time import sleep
import random
from communicator import Communicator

def test_valid_send():
    uuid = int(random.random()*99999999)
    c0 = Communicator(0, uuid)
    c1 = Communicator(1, uuid)

    c0.send_message(1, 'test message')
    sleep(2)
    res, queue_len = c1.get_message()
    
    assert res == 'test message'
    assert queue_len == 1

def test_empty_receive():
    uuid = int(random.random()*99999999)
    c0 = Communicator(0, uuid)

    res, queue_len = c0.get_message()

    assert res is None
    assert queue_len == 0

def test_multiple_messages():
    uuid = int(random.random()*99999999)
    c0 = Communicator(0, uuid)
    c1 = Communicator(1, uuid)
    
    for i in range(50):
        c0.send_message(1, 'test message %d' % i)
    res, queue_len = c1.get_message()
    
    assert res == 'test message 0'
    assert queue_len == 50


def test_multiple_receives():
    uuid = int(random.random()*99999999)
    c0 = Communicator(0, uuid)
    c1 = Communicator(1, uuid)
    
    for i in range(50):
        c0.send_message(1, 'test message %d' % i)

    for i in range(10):
        res, queue_len = c1.get_message()
    
    assert res == 'test message 9'
    assert queue_len == 41
