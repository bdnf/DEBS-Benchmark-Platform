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
import requests
pymysql.install_as_MySQLdb()


HOST = "http://127.0.0.1:8080"
PATH = '/schedule'

LOG_FOLDER_NAME = "scheduler_logs"
if not os.path.exists(LOG_FOLDER_NAME):
    os.makedirs(LOG_FOLDER_NAME)
filename='/scheduler.log'
logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s',
                    handlers=[
                     logging.FileHandler("{0}/{1}".format(LOG_FOLDER_NAME, filename)),
                     logging.StreamHandler()
                    ])
logger = logging.getLogger()

endpoint = os.getenv("FRONTEND_SERVER")
if endpoint is None:
    logger.error("please specify front-end server address!")
    #exit(1)
    endpoint = HOST + PATH
else:
    endpoint = "http://" + endpoint + PATH


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
            user = root
            password = os.getenv('MYSQL_ROOT_PASSWORD')
            dbase = os.getenv('MYSQL_DATABASE')
            logger.info(host, port, user, password, dbase)

            path = 'mysql://'+ user +':'+ password + '@'+ host +':' + str(port) + '/' + dbase
            logger.info(path)
            db = dataset.connect(path)
            self.table = db['teams']
            self.scheduled = []
            self.crawler = DockerCrawler(self.table)
        #return connection

    def __init__(self):

        json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
        self.schedule = {}
        try:
            self.schedule, _ = self.reguest_all_images()
        except requests.exceptions.ConnectionError as e:
            logger.error("Make sure that server you are trying to connect is up. %s" % e)
            logger.error("Please restart Scheduler when the frontend server is up!")
            logger.error("Hint! You can use 'docker restart scheduler' command.")
            exit(1)
        self.last_updated_images = {}
        self.crawler = DockerCrawler()
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
    def reguest_all_images(self):
        response = requests.get(endpoint)
        logger.info(response.status_code)
        schedule = response.json()
        logger.info("Scheduled images are: %s " % schedule)
        return schedule, response.status_code


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
        #self.all_teams = self.table.distinct('name')
        self.updated_status = False
        updated_images = []
        logger.info(self.schedule)
        for image, status in self.schedule.items():
                logger.info('updated: %s' % image)
                old_timestamp = self.last_updated_images.get(image)
                new_timestamp = self.crawler.run(image)
                if old_timestamp == new_timestamp:
                    logger.info('same')
                    self.updated_status =  False
                    if self.schedule.get(image) != 'old' and not None:
                        self.schedule[image] = 'old'
                elif old_timestamp is None and status == 'old':
                    #do nothing, only save timestamp as current one
                    print("all images are same")
                    self.last_updated_images[image] = new_timestamp
                    self.updated_status =  True
                else:
                    logger.info('new tag %s' % new_timestamp)
                    self.last_updated_images[image] = new_timestamp
                    self.updated_status =  True
                    self.schedule[image] = 'updated'
        #new_images = {}
        #for image in self.schedule:
                #print("docker_hub_link", docker_hub_link)

                    # except IndexError as e:
                    #     print(e)
                    #
                    #     print('Incorrectly specified image encountered. Format is {team_repo/team_image}')
                    #     print( t['team_image_name'].split('/')[1])
                    #     continue
        logger.info("all teams checked")
        #print('new_images', new_images)
        #self.last_updated_images = new_images

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

def send_schedule(payload):
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(endpoint, json = payload, headers=headers)

        logger.info('Response status is: %s' % response.status_code)
        if (response.status_code == 201):
            return {'status': 'success', 'message': 'updated'}
        if (response.status_code == 404):
            return {'message': 'Something went wrong. No scene exist. Check if the path is correct'}
    except requests.exceptions.ConnectionError as e:
        logger.error("please specify front-end server address! %s" % e)
        exit(1)
    return response.status_code

if __name__ == '__main__':
    logger.info("Waiting for DB server to start")
    logging.info("Waiting for the backend server to start")
    backoff = int(os.getenv("SCHEDULER_STARTUP_BACKOFF", default=30))
    frontend_backoff = int(os.getenv("FRONTEND_STARTUP_BACKOFF", default=0))
    if backoff <= frontend_backoff:
        logger.info("Sheduler should start after the frontend server. Correcting")
        backoff = frontend_backoff + 15
    time.sleep(backoff)
    # try:
    scheduler = Scheduler()
    # except requests.exceptions.ConnectionError:
    #     logging.warning("backing off creation of Scheduler. Could not reach server on first try")
    #     time.sleep(20)
    #     try:
    #         scheduler = Scheduler()
    #     except requests.exceptions.ConnectionError:
    #         logging.warning("backing off creation of Scheduler. Could not reach server on second try")
    #         time.sleep(30)
    #         scheduler = Scheduler()

    wait_seconds = int(os.getenv("SCHEDULER_SLEEP_TIME", default=5))
    wait_upper_bound = wait_seconds*10
    wait_lower_bound = wait_seconds

    while(True):
        #scheduler.connect_to_db()
        scheduler.run()
        updated_images = {}
        if scheduler.updated_status:
            for image, status in scheduler.schedule.items():
                    if status == 'updated':
                        updated_images[image] = scheduler.last_updated_images[image]
            wait_seconds = wait_lower_bound

        if updated_images:
            logger.info("sending images: ", updated_images)
            send_schedule(updated_images)
        else:
            logger.info("Images weren't updated yet")
            wait_seconds += 10
            if wait_seconds > wait_upper_bound:
                wait_seconds = wait_lower_bound

        #print("idling...")
        # updated = scheduler.get_schedule()
        # for image in updated:
        #     print("Updated image: %s by %s updated: %s" % (image['team_image_name'],image['name'], image['updated'] ))
        # #print(scheduler.get_schedule_as_json())
        time.sleep(wait_seconds)

    atexit.register(exit_handler)

# requests.exceptions.SSLError:
# HTTPSConnectionPool(host='hub.docker.com', port=443):
# Max retries exceeded with url: /v2/repositories/olehbodunov/sleepy_client/tags/
# (Caused by SSLError(SSLEOFError(8, u'EOF occurred in violation of protocol (_ssl.c:590)'),))
