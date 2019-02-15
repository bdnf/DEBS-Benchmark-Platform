import logging
import subprocess
import sqlite3
import os
import sys
import dataset
import json
import datetime
from crawler import DockerCrawler
import time
import pymysql
import atexit
import sqlalchemy

pymysql.install_as_MySQLdb()

class Scheduler:

    def connect_to_db(self):
        host = 'localhost'
        port = 3306
        user = 'dbuser'
        password = 'dbpassword'
        dbase = 'teams'
        path = 'mysql://'+ user +':'+ password + '@'+ host +':' + str(port) + '/' + dbase

        if 'MYSQL_ROOT_PASSWORD' not in os.environ:
            connection = dataset.connect(path)
        else:
            host = os.getenv('MYSQL_HOST')
            port = os.getenv('MYSQL_PORT')
            user = os.getenv('MYSQL_USER')
            password = os.getenv('MYSQL_PASSWORD')
            dbase = os.getenv('MYSQL_DATABASE')
            print(host, port, user, password, dbase)

            path = 'mysql://'+ user +':'+ password + '@'+ host +':' + str(port) + '/' + dbase
            print(path)
            db = dataset.connect(path)
            self.table = db['teams']
            self.scheduled = []
            self.crawler = DockerCrawler(self.table)
        #return connection

    def __init__(self):
        json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
        # db = os.getenv('TEAM_DB_URI')
        # if not db:
        #     db = "../db/teams.db"
        # #print("db path is:", db)
        # db = dataset.connect('sqlite:///'+db)
        #db = self.connect_to_db()
        # self.table = db['teams']
        # self.scheduled = []
        # self.crawler = DockerCrawler(self.table)
        #self.all_teams = self.table.distinct('name')

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
        self.all_teams = self.table.distinct('name')
        for team in self.all_teams:
            #print("team here:", team)
            query = self.table.find(name=team['name'])
            for t in query:
                #print("entry ", t['team_image_name'])
                if t['team_image_name']:
                    # try:
                        docker_hub_link = t['team_image_name'].split('/')
                        #print("docker_hub_link", docker_hub_link)
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
def exit_handler():
    print('My application is ending!')


if __name__ == '__main__':
    #print("Postponing container to start only after mysql is initialized")
    #time.sleep(5)
    try:
        try:
            time.sleep(8)
            scheduler = Scheduler()
        except (sqlalchemy.exc.OperationalError, pymysql.err.OperationalError, pymysql.ProgrammingError, pymysql.InternalError,
                        pymysql.IntegrityError, TypeError) as e:
            print(e)
            print("backing off connection for 10 seconds")
            time.sleep(10) #backoff
            scheduler = Scheduler()
    except Exception as e:
        print("backing off connection for 15 seconds")
        time.sleep(15)
        scheduler = Scheduler()

    while(True):
        scheduler.connect_to_db()
        scheduler.run()
        updated = scheduler.get_schedule()
        for image in updated:
            print("Updated image: %s by %s updated: %s" % (image['team_image_name'],image['name'], image['updated'] ))
        #print(scheduler.get_schedule_as_json())
        time.sleep(5)
        sys.stdout.flush()

    atexit.register(exit_handler)
