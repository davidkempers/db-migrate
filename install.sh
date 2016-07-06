#!/bin/bash

# remove the old container. will silently fail if a dbmigrate container exists
docker rmi dbmigrate &> /dev/null
docker build -t dbmigrate .
chmod +x ./bin/dbmigrate
cp ./bin/dbmigrate /usr/local/bin/dbmigrate
