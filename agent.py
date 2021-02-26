from communicator import Communicator

class Agent():
    def __init__(self, port, lifetime, logbook_name, ):
        # start a process for communication
        self.communicator = Communicator(machine_index, num_connections)
        # start listening

        # generate a speed, logbook
        self.speed = 0
        self.logbook = None

        self.communicator.make_connections()

        self.main_loop(lifetime)


    def main_loop(self, lifetime):
        pass


    def log_activity(self):
        pass
