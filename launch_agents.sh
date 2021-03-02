#!/bin/bash

_term() {
    echo "Caught SIGTERM or SIGINT signal!"

    for job in `jobs -p`
    do
        kill -TERM $job 2>/dev/null
    done
  exit 0
}

trap _term SIGTERM
trap _term SIGINT

python agent.py 60 0 3 &
python agent.py 60 1 3 &
python agent.py 60 2 3 &

for job in `jobs -p`
do
    wait $job
done
