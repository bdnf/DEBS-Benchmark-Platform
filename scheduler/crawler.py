import requests
import datetime
import dataset
import os

DOCKER_REGISTRY_V2 = 'https://hub.docker.com/v2/repositories'


class DockerCrawler:

    def __init__(self, table):
        #db = dataset.connect('sqlite:///'+db)
        self.table = table

    def convert_time(self, s):
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')

    def run(self, team_repo, team_image):
        url = DOCKER_REGISTRY_V2 + '/%s/%s/tags/'%(team_repo, team_image)
        print("requesting: ", url)
        data = requests.get(url)
        if data.status_code >= 400:
            print(data.status_code)
            return
        last_updated = data.json()['results'][0]['last_updated']
        previously_updated  = self.table.find(team_image_name= team_repo +'/'+ team_image)
        entry = list(previously_updated)
        try:
            previous_time_tag = entry[0]['time_tag']
            print("previous", previous_time_tag)
            if self.convert_time(last_updated) != previous_time_tag:
                print("Image was updated at %s" % self.convert_time(last_updated))
                self.table.update(dict(name=entry[0]['name'],
                                    team_image_name= team_repo +'/'+ team_image,
                                    time_tag = self.convert_time(last_updated),
                                    updated='True'), ['name', 'team_image_name'])
            else:
                print('tag was not changed')
        except KeyError:
            # it is first entry
            print("!tag is new")
            self.table.update(dict(name=entry[0]['name'],
                                team_image_name= team_repo +'/'+ team_image,
                                time_tag = self.convert_time(last_updated),
                                updated='True'), ['name', 'team_image_name'])




team_repo = 'debs2019challenge'
team_image = 'benchmark-server'

# data = requests.get(url)
#
#
# print(convert(last_updated))
#
# newly_updated = data.json()['results'][0]['last_updated']
#
# print(last_updated == newly_updated)
#
# #team = table.find_one(name='TU Berlin')
# table.update(dict(name='TU Berlin',
#                     timestamp = convert(last_updated),
#                     team_image_name='',
#                     updated='True'), ['name'])
#
# print("check")
# pick_b = table.find()
# for t in pick_b:
#     print(t['name'], t['timestamp'])
