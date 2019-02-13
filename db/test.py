import dataset
import json
import datetime
from time import gmtime, strftime
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv, find_dotenv

# from pathlib import Path  # python3 only
# env_path = Path('..') / '.env'
# load_dotenv(dotenv_path=env_path)
#
db = os.getenv('TEAM_DB_URI')
print('env is: ', db)
if db is None:
    db = "../db/teams.db"
# print(os.environ.get('TEAM_DB_URI'))
db = dataset.connect('sqlite:///'+db)
'''
schema

|team-name|team-image-name|image-tag|accuracy|precision|recall|runtime|scenes_processed|

'''

table = db['teams']
# all = table.all('tag')
# print(list(all))
all = table.distinct('team_image_name')
img =[]
for t in all:
    img.append(t['team_image_name'])
print(img)

query = 'SELECT name,team_image_name,accuracy,precision,recall,scenes_processed,runtime, updated FROM teams ORDER BY runtime DESC'
result = db.query(query)
ranking = {}
for ix, row in enumerate(result):
   ranking[ix+1] = row
print(ranking)
#print([i['name'] for i in list(all)])
# check = table.find(recall=0.6)
# print(list(check)[0]['recall'])
# nulls = table.delete(container="")
# table.delete(team_image="")
# #table.insert(dict(name='TU Berlin', updated="True"))
# table.update(dict(name='TUD', acc=0.21, recall=0.33), ['name'])
# table.update(dict(name='TU Berlin', acc=0.34, recall=0.60,team_image_name='tub/tud-benchm', timestamp=datetime.datetime.utcnow()), ['name'])
