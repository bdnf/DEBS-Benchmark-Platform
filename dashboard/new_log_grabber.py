import json
import sys
import os
from random import randint

print("Starting")
rootdir = "../logs"
overall_data = {}

for subdir, dirs, files in os.walk(rootdir):
    for dir in dirs:
        #if "logs" in dir:
        print("Curdir: ", dir)
        list_of_files = os.listdir(rootdir+"/"+dir)
        list_of_files = [i for i in list_of_files if ".json" in i]
        if not list_of_files:
            continue
        fresh_log = list_of_files[0]
        print(fresh_log)

        with open(rootdir + "/"+ dir+ "/"+fresh_log) as f:
            data = json.load(f)
            print("data here is: ", data)
            key = dir
            if not key:
                key = 'unknown_team_'+str(randint(0, 9))
            overall_data[key] = data
            
print(overall_data)
