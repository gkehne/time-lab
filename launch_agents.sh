#!/bin/bash

_term() {
    echo "Caught SIGTERM or SIGINT signal!"

    for job in `jobs -p`
    do
        kill $job 2>/dev/null
    done
  exit 0
}

trap _term SIGTERM
trap _term SIGINT

TIME=$(date +%s)

python agent.py 60 0 3 $1 $TIME &
python agent.py 60 1 3 $(($1+1)) $TIME &
python agent.py 60 2 3 $(($1+2)) $TIME &

for job in `jobs -p`
do
    wait $job
done
