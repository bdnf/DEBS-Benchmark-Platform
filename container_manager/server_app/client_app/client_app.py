import requests

import os

import sys
import csv
out_file = "./dataset/out.csv"
import subprocess
from random import randint
import time

def read_csv(out_file, scene):
        with open(out_file, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                scene_index = float(line[0])
                if scene_index == scene:
                    return line[1:]

def list_to_dict(a):
    my_dict = {}
    for index, item in enumerate(a):
        if index % 2 == 0:
            my_dict[item] = a[index+1]
    return my_dict


def host_url(host, path):
    return "http://" + host + path


def get_scene(host):
    return requests.get(host_url(host, '/scene/'))


def post_answer(host, payload):
    headers = {'Content-type': 'application/json'}
    response = requests.post(host_url(host, '/scene/'), json = payload, headers=headers)

    print('Response status is: ', response.status_code)
    if (response.status_code == 201):
        return {'status': 'success', 'message': 'updated'}
    if (response.status_code == 404):
        return {'message': 'Something went wrong. No scene exist. Check if the path is correct'}


if __name__ == "__main__":
    print('ENV is ', os.getenv('BENCHMARK_SYSTEM_URL'))
    #print(subprocess.check_output(['ls']))

    host = os.getenv('BENCHMARK_SYSTEM_URL')
    if host is None or '':
        print('Error reading Server address!')

    print('Getting scenes for predictions...')
    time.sleep(5)
    # Here is an automated script for getting all scenes
    # and submitting prediction for each of them
    # you may change to fit your needs
    scene = 0
    while(True):

        # Making GET request
        # Each request will fetch new scene
        response = get_scene(host)
        if response.status_code == 404:
            print(response.json())
            sys.stdout.flush()
            break

        data = response.json()

        # example of reconstruction json payload from GET request into DataFrame
        #reconstructed_scene = pd.read_json(data['scene'], orient='records')
        random_scene = randint(0, 499)
        # a = read_csv(out_file, random_scene % 500)
        # example_result = list_to_dict(a)
        # print("example ", example_result)
        # time.sleep(randint(0,3))
        # if scene % 10 == 0:
        #     time.sleep(randint(10,20))
            #raise Exception("randomly killing the container")
        # DO YOUR PREDICTIONS HERE
        # return the result in format in plain json:
        # for example:
        example_result = {'car': 1, 'armchair': 2}
        # after making sure the result in correct form you need to submit it
        # via POST request:
        post_answer(host, example_result)
        scene += 1

    print('Submission for all scenes done successfully!')
