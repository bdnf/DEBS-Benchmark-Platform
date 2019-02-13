import dataset
import json

db = dataset.connect('sqlite:///teams.db')
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

#table.update(dict(name='TUD', team_image_name='val', updated='False'), ['name'])

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
    if t['name'] == 'TU Darmstadt':
        table.update(dict(name=str(t['name']), updated='True'), ['name'])
#print(json.dumps(pick_tud))
print("check")
pick_b = table.find(name='TU Berlin')
print(list(pick_b))
