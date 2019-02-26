#!/bin/bash
echo "Enter full folder path for data .csv files: $KEEPTHISMESSAGE"
#echo "Type the new message that you want to enter, followed by [ENTER]:"
read KEEPTHISMESSAGE
export HOST_DATASET_FOLDER=$KEEPTHISMESSAGE
echo "Enter full folder path where log files will be stored. Suggestion $pwd/logs: $LOGFOLDER"
read LOGFOLDER
export HOST_LOG_FOLDER=$LOGFOLDER
source ./server_app/test.env
echo "Checking"
echo $HOST_DATASET_FOLDER
echo $HOST_LOG_FOLDER
