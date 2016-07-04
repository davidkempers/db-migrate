#!/bin/bash

# entry point script for docker

cmd=$1

if [[ $cmd == "update" ]]; then
    python ./migrate.py {$@}
elif [[ $cmd == "rollback" ]]; then
    python ./migrate.py {$@}
elif [[ $cmd == "diff" ]]; then
    python ./migrate.py {$@}
elif [[ $cmd == "generate" ]]; then
    python ./generate.py {$@}
elif [[ $cmd == "dump" ]]; then
    python ./dump.py {$@}
fi
