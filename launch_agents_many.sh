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
LIFETIME=180

# $1 is the global seed
# $2 is the randint_max value

# args: lifetime, machine_index, num_machines, seed, sys_time, randint_max, ticks_per_second
python agent.py $LIFETIME 0 12 $1 $TIME $2 4 &
python agent.py $LIFETIME 1 12 $(($1+1)) $TIME $2 4 &
python agent.py $LIFETIME 2 12 $(($1+2)) $TIME $2 4 &
python agent.py $LIFETIME 3 12 $(($1+3)) $TIME $2 4 &
python agent.py $LIFETIME 4 12 $(($1+4)) $TIME $2 4 &
python agent.py $LIFETIME 5 12 $(($1+5)) $TIME $2 4 &
python agent.py $LIFETIME 6 12 $(($1+6)) $TIME $2 4 &
python agent.py $LIFETIME 7 12 $(($1+7)) $TIME $2 4 &
python agent.py $LIFETIME 8 12 $(($1+8)) $TIME $2 4 &
python agent.py $LIFETIME 9 12 $(($1+9)) $TIME $2 4 &
python agent.py $LIFETIME 10 12 $(($1+10)) $TIME $2 4 &
python agent.py $LIFETIME 11 12 $(($1+11)) $TIME $2 4 &

for job in `jobs -p`
do
    wait $job
done
