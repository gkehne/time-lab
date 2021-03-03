# CS262 assignment 2


## Setup

The message passing is based on a RabbitMQ message broker and the `pika` python package client. Running the code requires a RabbitMQ server, there are a few ways to run this but we've found the pre-built docker container works very easily:

```
docker run -it --rm tmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

or alternatively:

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

This requires docker to be installed and running, you can read about how to set that up here: https://www.docker.com/get-started. Alternatively, guides for downloading and installing rabbitmq outside of docker can be found here: https://www.rabbitmq.com/download.html.

### Python

We'll also need Python 3.7.

An easy way to manage dependencies is to maintain a virtual environment for all machines which will be running the client or the server.
Although it's perhaps overkill, for this purpose we recommend [installing conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

Once `conda` is installed, it can be used to create an environment by running
 ```bash
 conda create --name chatenv python=3.7
 ```
 followed by
 ```bash
 conda activate chatenv
 ```
(to exit simply type `conda deactivate`).

We will also need the `pika` and `pytest` packages. With the conda environment active, run

```
pip install pika pytest
```

## Running the program

1. Start the RabbitMQ broker server. Either run the docker command above or if you installed it yourself, start the server on the default port.
2. Run `./launch_agents.sh <global seed> <randint_max>`

`<global seed>` should be an integer which sets the global seed, in turn setting the seeds of each of the agents. This can be any integer; use the same integer to get reproducible results.

`<randint_max>` should be the integer upper bound (inclusive) for the random action taken by each agent. Specifically, when an agent's queue is empty it selects an integer from 1 to `<randint_max>`. If the integer is in \[1, 3\], it performs some type of send command. If the integer is in \[4, `<randint_max>`\], it sends nothing. In any case, the agent always updates its clock and logs.

### Tests

Running tests also requires the RabbitMQ broker server to be running. To run the tests, simply call

```
pytest
```

## Design decisions

Early on, it was clear that we would need three core components: an `Agent` object that would form a single virtual machine, a way of starting multiple agents, and a way for the agents to communicate.

### Agent

The core class representing a virtual machine is the `Agent` class. The `Agent` is responsible for setting up the clock cycle, executing commands at the correct frequency, and handling the logic for the program. To run at a specific clock freqency, we decided to use python's `sleep` function to wait the appropriete amount of time between executions. We found that because of the communication approach we used (described below), the "work" at a given cycle actually took a small but measurable amount of time that added up over the 100s of iterations. To avoid the global time from drifting too much, we therefore improved the accuracy by capturing the system time before work was done and taking this into account when deciding how much time to wait.

The logic for the agent is simply exactly as described in the assignment, with the agent receiving a message if one was available and either working or sending a message if not. For logging, we decided to use a simple csv which the agent appends to. To make everything reproducible we initialize the agent with a controlled seed.

### Launching

We wanted it to be easy to start multiple agents at almost exactly the same time. We considered using multiprocessing to handle this, but decided that added unneeded complication. We thought it would be much easier to simple have a bash script that starts the processing in the background, which turned into `launch_agents.sh`. We wanted the entire process to be reproducible, but we also wanted the agents to not all have the same seed so their clock rates would not all be the same. To accomplish this we defined a global seed which is passed into the bash script, which deterministically sets different values for each agent's seed. To ease experimenting with different amounts of passive "work," `launch_agents.sh` also takes a second argument which is the maximum integeter for the agent's random action selection process.

Additionally, to ease experimentation, we put in a little effort to make the bash script launch the agents at the same time but wait to exit until they are all finished. Furthermore, we handle `SIGINT` called with Ctrl+C to kill any remaining agent processes.

### Communication

We considered a few options for communication between the agents; we wanted a form of communication that was easy to setup and relatively lightweight but would allow the agents to robusting send messages to each other. We settled on [RabbitMQ](https://www.rabbitmq.com/), which is the backend message broker. Running the system requires first running the broker in a separate process. Once this is running, we use the python client `pika` to interface with the broker to send and receive messages. RabbitMQ handles communication in a publish/subscribe model, where all communication is to and from queues. We adapt that to messages between agents by assigning each agent a queue based on the agents unique index. To send a message to the agent one sends a message to the corresponding queue, and each agent is continuously listening to events on their queue.

The communication is manifested through the `Communicator` class in `communicator.py`. In order to both listen for new messages and send messages we use blocking connections and multiprocessing. Specifically, a child process runs which listens for messages to the broker queue, adding them to a multiprocessing queue. It turned out that querying for the length of a standard `multiprocessing.Queue` is not implemented on Mac (which is crazy), so we had to make our own `Queue` class that handled querying for the length properly. To match the specification, `Communicator` implements a `get_message()` function which pops any incoming messages off the multiprocessing queue and returns it, or None otherwise.

Initially, we thought we might need to handle edge cases where messages are incoming to agents that don't exist yet. Because of the queue-based communication via the message broker, however, this problem is alleviated by declaring broker queues on both the sending and recieving ends of the communication. This way, if the receiving agent doesn't exist yet, the message is still added to the correct queue and the receiver receives the message as soon as it starts listening. This allowed us to simple start all the agents at roughly the same time without caring for the exact order or needed to verify that all agents were ready.

One last challenge we ran into was that originally, the queue names were exactly the machine indices. Because the broker was persistent and the machines weren't all ending at exactly the same time, often the broker queues were left with lingering messages from previous experiments, which jumped the logical clocks forward significantly. To get around this, we simply added a `uuid` portion to the queue name, with the `uuid` being the same for all three agents for a run, coming from the integer second since the unix epoch the agents were launched.

## Experiments
