import json
import sys
import os
from random import randint
import dataset

def new_result_grabber():
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
            runtime = 0
            accuracy = 0
            recall = 0
            precision = 0
            computed_scenes = 0

            with open(rootdir + "/"+ dir+ "/"+fresh_log) as f:
                data = json.load(f)
                print("data here is: ", data)
                key = dir
                if not key:
                    key = 'unknown_team_'+str(randint(0, 9))
                overall_data[key] = data
                print(data['runtime'])
                runtime = data['runtime']
                accuracy = data['accuracy']
                recall = data['recall']
                precision = data['precision']
                computed_scenes = data['computed-scenes']

            db = dataset.connect('sqlite:///../db/teams.db')
            table = db['teams']
            all = table.distinct('team_image_name')
            img =[]
            for t in all:
                img.append(t['team_image_name'])
            print(img)
            for i in img:
                if dir in i:
                    print("Yep: %s is in %s "% (dir,i))
                    #table.find(team_image_name=i)
                    table.update(dict(team_image_name=i,
                                    runtime = runtime,
                                    accuracy = accuracy,
                                    recall = recall,
                                    precision = precision,
                                    scenes_processed = computed_scenes
                                ), ['team_image_name'])

    # def generate_ranking_table():
    #     query = 'SELECT name,team_image_name,accuracy,precision,recall,scenes_processed,runtime, updated FROM teams ORDER BY runtime DESC'
    #     result = db.query(query)
    #     ranking = {}
    #     for ix, row in enumerate(result):
    #        ranking[ix+1] = json.dumps(row)
    #     return ranking

    print(overall_data)
