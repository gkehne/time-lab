# rabbitMQ
import pika
import multiprocessing as mp
from queue_with_size import Queue
import sys


def listen_for_messages(q, machine_index):
    def callback(ch, method, properties, body):
        q.put(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)
    
    # Setup connection to listen to
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=str(machine_index))
    channel.basic_consume(queue=str(machine_index), on_message_callback=callback)

    # Start listening
    channel.start_consuming()

class Communicator():
    def __init__(self, machine_index, num_machines):
        self.machine_index = machine_index
        self.num_machines = num_machines

        # Setup message queue
        self.message_queue = Queue()

        # Setup message listener process
        self.message_listener = mp.Process(target=listen_for_messages, args=(self.message_queue, self.machine_index))
        self.message_listener.daemon = True
        self.message_listener.start()

    def send_message(self, recipient, msg):
        # recipient is the machine ID as an int

        # We're going to setup a connection, send, and kill the connection when sending each message
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=str(recipient))
        channel.basic_publish(exchange='', routing_key=str(recipient), body=msg.encode())
        connection.close()

    def get_message(self):
        queue_len = self.message_queue.qsize()
        if self.message_queue.empty():
            return None, queue_len
        
        return self.message_queue.get().decode(), queue_len


if __name__ == '__main__':
    machine_index = int(sys.argv[1])
    num_machines = int(sys.argv[2])
    send = bool(int(sys.argv[3]))

    comm = Communicator(machine_index, num_machines)

    if send:
        comm.send_message((machine_index+1) % num_machines, 'test message')

    while True:
        pass
