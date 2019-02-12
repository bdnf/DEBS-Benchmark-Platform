import os
import json
from random import randint
import subprocess
from flask import Flask, jsonify, Response, escape, render_template
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from docker_client import start
import time
import html
from textwrap import dedent
app = Flask(__name__)

print("Starting")
rootdir = "./"

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


@app.route('/result', methods=['GET'])
def get():
        data = extract_results_from_json()
        print(data)
        return render_template('table.html', post=data)
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
