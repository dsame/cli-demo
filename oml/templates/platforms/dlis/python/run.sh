#####################
#### DO NOT EDIT ####
#####################

#!/bin/bash
# The following is necessary because docker, by default, does not execute any bashrc or profile source when "xxx.sh" is used as the start command
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

#turn on job control in script
argumentation= ''
if [ "$1" == "grpc" ]
then
	python3 /model/code/grpc_server.py $argumentation
elif [ "$1" == "http" ]
then
	python3 /model/code/http_server.py $argumentation
elif [ "$1" == "offline" ]
then
	python3 /model/code/offline_process.py $2 $3 $argumentation
else
	echo "usage:"
	echo $1
	echo "1. ./run.sh grpc"
	echo "2. ./run.sh http"
	echo "3. ./run.sh offline inputfile outputfile"
	exit 1
fi