import os
import json
from random import randint
import subprocess
from flask import Flask, jsonify, Response, escape, render_template
import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#from docker_client import start
import time
import html
from textwrap import dedent
import dataset
import datetime

app = Flask(__name__)

print("Starting")
rootdir = "../"

def new_result_grabber(table):
    print("Starting grabbing results")
    logdir = "./logs"
    overall_data = {}

    for subdir, dirs, files in os.walk(logdir):
        for dir in dirs:
            #if "logs" in dir:
            print("Curdir: ", dir)
            list_of_files = os.listdir(logdir+"/"+dir)
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

            with open(logdir + "/"+ dir+ "/"+fresh_log) as f:
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

            #db = dataset.connect('sqlite:///../db/teams.db')
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
    print("completed grabbing")
    #print(overall_data)

def extract_results_from_logs():
    for subdir, dirs, files in os.walk(rootdir):
        for dir in dirs:
            if "logs" in dir:
                print("Yes it starts", dir)
                list_of_files = os.listdir(rootdir+dir)
                list_of_files = [i for i in list_of_files if ".log" in i]
                fresh_log = list_of_files[-1]
                print(fresh_log)
                result = []
                with open(rootdir + dir+ "/"+fresh_log) as search:
                    for line in search:
                        line = line.rstrip()  # remove '\n' at end of line
                        if "FINAL_RESULT" in line:
                            result_line = line.split("FINAL_RESULT")[1]
                            print(result_line)
                            result.append(result_line)
                print(result)
                if result:
                    data = {
                        "team": {
                            "name": dir.split("logs")[1],
                            "accuracy": result[0][-3:],
                            "runtime": result[1][-2:]
                        }
                    }
                    print(data)

def extract_results_from_json():
    overall_data = {}
    for subdir, dirs, files in os.walk(rootdir):
        for dir in dirs:
            if "logs" in dir:
                print("Yes it starts", dir)
                list_of_files = os.listdir(rootdir+dir)
                list_of_files = [i for i in list_of_files if ".json" in i]
                if not list_of_files:
                    continue
                fresh_log = list_of_files[0]
                print(fresh_log)

                with open(rootdir + dir+ "/"+fresh_log) as f:
                    data = json.load(f)
                    key = dir.split("logs")[1][1:]
                    if not key:
                        key = 'unknown_team_'+str(randint(0, 9))
                    overall_data[key] = data
    return overall_data

def generate_ranking_table():
    db = os.getenv('TEAM_DB_URI')
    print('env is: ', db)
    if db is None:
        db = "../db/teams.db"
    # print(os.environ.get('TEAM_DB_URI'))
    print('sqlite:///'+db)
    db = dataset.connect('sqlite:///'+db)
    table = db['teams']
    new_result_grabber(table)
    all = table.distinct('team_image_name')
    query = 'SELECT name,team_image_name,accuracy,precision,recall,scenes_processed,runtime, updated FROM teams ORDER BY runtime DESC'
    result = db.query(query)
    ranking = {}
    queue = []
    delta = datetime.timedelta(minutes=15)
    time = datetime.datetime.utcnow() + delta
    marked = 0
    for ix, row in enumerate(result):
       ranking[ix+1] = row
       if row['updated']  == "True":

           queue.append({row['name']: unconvert_time(time + delta*(marked))  })
           marked +=1
    #print(ranking)
    return ranking, queue

def unconvert_time(s):
    return s.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/result', methods=['GET'])
def get():

        #data = extract_results_from_json()
        data, queue = generate_ranking_table()
        print(queue)
        #print(data[1])
        for k,v in data.items():
            print(v['name'], v['accuracy'], v['runtime'])

        return render_template('table.html', post=data, team=queue)
        #with open('overall_result.json', 'w') as outfile:
        #    json.dump(data, outfile)
        #return jsonify(data)



def stream(generator):
    """Preprocess output prior to streaming."""

    for line in generator:
        yield escape(line.decode('utf-8'))  # Don't let subproc break our HTML


@app.route('/start', methods=['GET'])
def index():
    def g():
        yield "<!doctype html><title>Stream subprocess output</title>"

        with subprocess.Popen([sys.executable or 'python', '-u', '-c', dedent("""\
            # dummy subprocess
            from docker_client import start
            start()
            """)], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                   bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                yield "<code>{}</code>".format(html.escape(line.rstrip("\n")))
                yield "<br>\n"
    return Response(g(), mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8110)
