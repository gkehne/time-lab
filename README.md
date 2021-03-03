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

## Running experiments

Start a rabbitmq server
call launch_agents.sh with these parameters and what they mean

## Design decisions

Early on, it was clear that we would need three core components: an `Agent` object that would form a single virtual machine, a way of starting multiple agents, and a way for the agents to communicate.

### Agent

The core class representing a virtual machine is the `Agent` class. The `Agent` is responsible for setting up the clock cycle, executing commands at the correct frequency, and handling the logic for the program. To run at a specific clock freqency, we decided to use python's `sleep` function to wait the appropriete amount of time between executions. We found that because of the communication approach we used (described below), the "work" at a given cycle actually took a small but measurable amount of time that added up over the 100s of iterations. To avoid the global time from drifting too much, we therefore improved the accuracy by capturing the system time before work was done and taking this into account when deciding how much time to wait.

The logic for the agent is simply exactly as described in the assignment, with the agent receiving a message if one was available and either working or sending a message if not. For logging, we decided to use a simple csv which the agent appends to. To make everything reproducible we initialize the agent with a controlled seed.

### Launching

We wanted it to be easy to start multiple agents at almost exactly the same time. We considered using multiprocessing to handle this, but decided that added unneeded complication. We thought it would be much easier to simple have a bash script that starts the processing in the background, which turned into `launch_agents.sh`. We wanted the entire process to be reproducible, but we also wanted the agents to not all have the same seed so their clock rates would not all be the same. To accomplish this we defined a global seed which is passed into the bash script, which deterministically sets different values for each agent's seed. To ease experimenting with different amounts of passive "work," `launch_agents.sh` also takes a second argument which is the maximum integeter for the agent's random action selection process.

Additionally, to ease experimentation, we put in a little effort to make the bash script launch the agents at the same time but wait to exit until they are all finished. Furthermore, we handle `SIGINT` called with Ctrl+C to kill any remaining agent processes.

### Communication

We considered a few options for communication between the agents; we wanted a form of communication that was easy to setup and relatively lightweight but would allow the agents to robusting send messages to each other. We settled on 

## Experiments
