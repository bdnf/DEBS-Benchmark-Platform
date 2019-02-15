import dataset
import json
import pymysql
import os

pymysql.install_as_MySQLdb()

host = 'localhost'
port = 3306
user = 'dbuser'
password = 'dbpassword'
dbase = 'teams'
path = 'mysql://'+ user +':'+ password + '@'+ host +':' + str(port) + '/' + dbase

psw = os.getenv('MYSQL_ROOT_PASSWORD')
if not psw:
    print(path)
    db = dataset.connect(path)
else:
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_ROOT_PASSWORD')
    dbase = os.getenv('MYSQL_DATABASE')

    path = 'mysql://'+ user +':'+ password + '@'+ host +':' + str(port) + '/' + dbase
    db = dataset.connect(path)

'''
schema

|name|team_image_name|tag|time_tag|updated(Bool)|accuracy|precision|recall|runtime|

scenes_processed|start_time|


olehbodunov/docker_api_python_client_test
olehbodunov/dataset-client
olehbodunov/docker_api_python_client
'''

table = db['teams']
# table.insert(dict(name='TU Dresden', team_image_name="olehbodunov/dataset-client"))
# table.insert(dict(name='TU Munich', team_image_name="olehbodunov/docker_api_python_client"))
# table.insert(dict(name='TU Berlin', team_image_name="olehbodunov/docker_api_python_client_test"))
# table.insert(dict(name='TU Jena', team_image_name="olehbodunov/failing_client"))
# table.insert(dict(name='TU Darmstadt', team_image_name="olehbodunov/random_client"))
# table.insert(dict(name='TU Karlsruhe', team_image_name="olehbodunov/sleepy_client"))

pick_one = table.find_one(name='TUD')

table.update(dict(name='TU Dresden', tag='sha256', scenes=50), ['name'])

pick_one = table.find_one(name='TUM')
pick_tud = table.find_one(name='TUD')
pick_b = table.find_one(name='TU Berlin')
print(pick_b)
# teams = db['teams'].find(updated='False')
teams = db['teams'].all()
# #print(list(teams))
#
for t in teams:
#     #print("Teams", t)
#     #print("name", t['name'])
    #if t['name'] == 'TU Darmstadt':
        table.update(dict(name=str(t['name']), updated='True'), ['name'])
#print(json.dumps(pick_tud))
print("check")
pick_b = table.find(name='TU Berlin')
print(list(pick_b))
