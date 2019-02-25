import requests
import datetime
import dataset
import os

DOCKER_REGISTRY_V2 = 'https://hub.docker.com/v2/repositories'


class DockerCrawler:

    def __init__(self):
        #db = dataset.connect('sqlite:///'+db)
        self.table = []

    def convert_time(self, s):
        myfmt = "%Y-%m-%d %H:%M"
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(microsecond=0).replace(second=0)

    def run(self, image):
        docker_hub_link = image.split('/')

        url = DOCKER_REGISTRY_V2 + '/%s/%s/tags/'%(docker_hub_link[0], docker_hub_link[1])
        #print("requesting: ", url)
        data = requests.get(url)
        if data.status_code >= 400:
            print("Can't access image. This image may be marked as private. Status: ", data.status_code)
            return
        last_updated = data.json()['results'][0]['last_updated']
        return self.convert_time(last_updated)
        #
        # previously_updated  = self.table.find(team_image_name= team_repo +'/'+ team_image)
        # entry = list(previously_updated)
        # last_updated = self.convert_time(last_updated)
        # try:
        #     previous_time_tag = entry[0]['time_tag']
        #     #datetime object we compare withour sec and ms
        #     #as mysql and dqlite differently stores datetime object
        #     #to convert to string use: .strftime("%Y-%m-%d %H:%M")
        #     previous_time_tag = previous_time_tag.replace(microsecond=0).replace(second=0)
        #     #print("previous entry: ", previous_time_tag)
        #     #print("last updated: ", last_updated)
        #     if last_updated != previous_time_tag:
        #         print("Image was updated at %s" % last_updated.strftime("%Y-%m-%d %H:%M"))
        #         self.table.update(dict(name=entry[0]['name'],
        #                             team_image_name= team_repo +'/'+ team_image,
        #                             time_tag = last_updated,
        #                             updated='True'), ['name', 'team_image_name'])
        #     else:
        #         print('tag has not changed for image: ', entry[0]['team_image_name'])
        # except KeyError:
        #     # it is first entry
        #     print("creating time_tag column")
        #     self.table.update(dict(name=entry[0]['name'],
        #                         team_image_name= team_repo +'/'+ team_image,
        #                         time_tag = last_updated,
        #                         updated='True'), ['name', 'team_image_name'])




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
