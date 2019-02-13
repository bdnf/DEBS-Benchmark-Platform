import logging
import subprocess
import sqlite3
import os
import dataset
import json
import datetime
from crawler import DockerCrawler
import time

class Scheduler:

    def __init__(self):
        json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
        db = os.getenv('TEAM_DB_URI')
        if not db:
            db = "../db/teams.db"
        #print("db path is:", db)
        db = dataset.connect('sqlite:///'+db)
        self.table = db['teams']
        self.scheduled = []
        self.crawler = DockerCrawler(self.table)
        self.all_teams = self.table.distinct('name')

    def check_tag(self):
        scheduled = self.table.find(updated='True')
        self.scheduled = list(scheduled)
        #self.mark_checked()

    def mark_checked(self):
        for team in self.scheduled:
            #print("Team name:", team['name'])
            self.table.update(dict(name=team['name'], team_image_name=team['team_image_name'], updated='False'), ['name', 'team_image_name'])

    def get_schedule(self):
        self.check_tag()
        return self.scheduled

    def get_schedule_as_json(self):
        self.check_tag()
        return json.dumps(self.scheduled)

    def update_scedule(self):
        self.check_tag()

    def run(self):
        for team in self.all_teams:
            print("team here:", team)
            query = self.table.find(name=team['name'])
            for t in query:
                print("entry ", t['team_image_name'])
                if t['team_image_name']:
                    # try:
                        docker_hub_link = t['team_image_name'].split('/')
                        print("docker_hub_link", docker_hub_link)
                        self.crawler.run(docker_hub_link[0], docker_hub_link[1])
                    # except IndexError as e:
                    #     print(e)
                    #
                    #     print('Incorrectly specified image encountered. Format is {team_repo/team_image}')
                    #     print( t['team_image_name'].split('/')[1])
                    #     continue
                else:
                    print('Team did not submitted image yet')
        print("all teams checked")

#get teams
#crawl
#if changed -> updated=True
#sleep(5)

#manager
#get teams
# if changed -> pull
#   set False, set ETS?

if __name__ == '__main__':
    #json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
    scheduler = Scheduler()
    while(True):
        scheduler.run()
        updated = scheduler.get_schedule()
        for image in updated:
            print("Updated image: %s by %s updated: %s" % (image['team_image_name'],image['name'], image['updated'] ))
        #print(scheduler.get_schedule_as_json())
        time.sleep(5)
