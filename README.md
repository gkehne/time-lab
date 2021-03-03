# time-lab
CS262 assignment 2

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

