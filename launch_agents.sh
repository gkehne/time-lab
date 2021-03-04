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

# $1 is the global seed
# $2 is the randint_max value

# agent.py args are lifetime, machine_index, num_machines, seed, randint_max
python agent.py 60 0 3 $1 $TIME $2 &
python agent.py 60 1 3 $(($1+1)) $TIME $2 &
python agent.py 60 2 3 $(($1+2)) $TIME $2 &

for job in `jobs -p`
do
    wait $job
done
