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
