import docker
import logging
import subprocess
import datetime
import sys, os
import yaml
import json
import re
from collections import OrderedDict
import dataset
import time

class Manager:

    def __init__(self):

        LOG_FOLDER_NAME = "manager_logs"
        if not os.path.exists(LOG_FOLDER_NAME):
            os.makedirs(LOG_FOLDER_NAME)
        logging.basicConfig(filename=LOG_FOLDER_NAME+'/compose_manager.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
        self.client = docker.from_env()
        json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
        db = os.getenv('TEAM_DB_URI')
        if not db:
            db = "../db/teams.db"
        #print("db path is:", db)
        db = dataset.connect('sqlite:///'+db)
        self.table = db['teams']
        self.images = []

    def execute(self, cmd):
        #prints output into console in real-time
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            #raise subprocess.CalledProcessError(return_code, cmd)
            logging.info("Docker-compose done executing")


    def create_docker_compose_file(self, image, container):
        mock_file = "docker-compose-mock.yml"
        logging.info("creating docker-compose with image: %s and container: %s " % (image, container))
        with open(mock_file) as f:
            list_doc = yaml.safe_load(f)
        list_doc["services"]["client"]["image"] = image
        list_doc["services"]["client"]["container_name"] = container
        volumes = list_doc["services"]["server"]["volumes"]
        log_volume = volumes[1].split(":")

        try:
            log_volume = log_volume[0]+ "/" + str(image.split("/")[1]) +":"+log_volume[1]
        except IndexError:
            log_volume = log_volume[0]+ "/" + str(image.split("/")[0]) +":"+log_volume[1]
        new_volumes = [volumes[0],log_volume]
        list_doc["services"]["server"]["volumes"] = new_volumes

        split_name = mock_file.split('.')
        new_name = "docker-compose.yml" #str(split_name[0]) + str(file_number) + "."+ str(split_name[1])

        with open(new_name, "w") as f:
            yaml.dump(list_doc, f, default_flow_style=False)
        logging.info("docker compose file saved with name %s" % new_name)
        #return new_name

    def get_schedule(self):
        scheduled_teams = self.table.distinct('name', updated='True')
        self.scheduled_teams = [ str(i['name']) for i in list(scheduled_teams) ]
        return self.scheduled_teams

    def uncheck_team(self, image):
        #self.images.remove(image)

        self.table.update(dict(team_image_name=image, updated='False'), ['team_image_name'])
        print("This image was unchecked: ", image)

    def compare_and_set(self, tag, image):
        print("Trying to untag: ", tag)
        try:
            old_tag = self.table.find(tag=tag)
            if old_tag['tag'] == tag:
                return False
            else:
                self.table.update(dict(name=old_tag['name'], tag=tag), ['name'])
                return True
        except Exception as e:
            print(e)
            self.table.update(dict(team_image_name=image, tag=tag), ['team_image_name'])
            print("tag updated")


    def get_images(self):
        for team in self.scheduled_teams:
            query = self.table.find(name=team)
            for t in query:
                print("entry ", t)
                if t['team_image_name']:
                    try:
                        docker_hub_link = t['team_image_name'].split('/')
                        self.images.append(str(t['team_image_name']))
                    except IndexError:
                        print('Incorrectly specified image encountered. Format is {team_repo/team_image}')
                        continue
                else:
                    print('Team did not submitted image yet')


    def grab_teams(self, teams_file):
        try:
            with open(teams_file.split('.')[0]+'.json') as f:
                data = json.load(f)
            return data

        except Exception as e:
            print(e)
            data = {}
            with open(teams_file) as f:
                for line in f:
                    line = re.sub(r"[,;\"\'\n\t\s]*", "",line)
                    data[line] = ""
            return data

    def start(self):

        #print(subprocess.check_output(['docker', 'version']))
        self.get_schedule()
        self.get_images()
        print("Got images; ", self.images)
        print("Got teams; ", self.scheduled_teams)
        # teams_file ='teams.txt'
        # repo_list = self.grab_teams(teams_file)
        # repo_list = OrderedDict(sorted(repo_list.items()))
        # print("Teams: ", repo_list)
        # print("Tags: ", repo_list.values())



        # client.images.pull('alpine')
        #
        # client.containers.list()

        docker_server_img_name = "benchmark-server"
        docker_container_name = "benchmark-server-logging"
        client_container_name = "client-app-"

        try:
            subprocess.check_output(['docker', 'rm', docker_container_name])
        except Exception as e:
            print(e)
            logging.warning("Container probably not exist yet %s" % e)
            pass

        for docker_img_name in self.images:

            print("trying with this name: ", docker_img_name)
            try:
                subprocess.check_output(['docker', 'rmi', docker_img_name])
            except Exception as e:
                print(e)
                pass
            try:
                print("Pulling image %s" % docker_img_name)
                self.client.images.pull(docker_img_name)
                tag = subprocess.check_output(['docker', 'inspect', docker_img_name])
                print('tagging: ')
                tag = json.loads(tag.decode('utf-8'))[0]["Id"]
                print(tag)
                if self.compare_and_set(tag, docker_img_name):
                    logging.info("Image is new! Updated tag for pulled image: %s" % docker_img_name)
                # if repo_list[docker_img_name] != tag:
                #     repo_list[docker_img_name] = tag
                #     print(repo_list)
                #     with open(teams_file.split('.')[0]+'.json', 'w') as outfile:
                #         json.dump(repo_list, outfile)
                #     logging.info("pulled image: %s" % docker_img_name)
            except Exception as e:
                logging.error("Error during pull happened %s" % e)
                print("Probably can't access image: %s. Error %s" % (docker_img_name, e))
                continue
            #new_img_name = docker_img_name.split("/")[1]# +"-"+ str(ix)
            try:
                img = self.client.images.get(docker_img_name)
            except docker.errors.ImageNotFound as e:
                logging.error("Error during pull happened %s" % e)

            # img.tag(new_img_name, tag= 'latest')
            # logging.info("tagged image: %s and tagged to: %s" % (docker_img_name, new_img_name))
            # subprocess.check_output(['docker' ,'rmi', docker_img_name])
            # logging.info("untagged old image %s" % docker_img_name)
            #new_container_name = docker_container_name + docker_img_name.split("/")[1]
            # print("Current dir is %s " % os.getcwd())

            self.create_docker_compose_file(docker_img_name, client_container_name+docker_img_name.split("/")[1]) #TODO change for [0] for client repo name
            logging.info("calling docker-compose -f  up ")

            # subprocess.check_output(['docker-compose' ,'up', '-d', '--build'])
            #subprocess.check_output(['docker-compose', 'up', '--build', '--abort-on-container-exit'])
            # = subprocess.Popen(,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cmd = ['docker-compose', 'up', '--build', '--abort-on-container-exit']
            # live console output
            for path in self.execute(cmd):
                print(path, "")
                logging.info(path)

            self.uncheck_team(docker_img_name)
            logging.info("docker-compose -f %s exited")



        # img = client.images.get(docker_img_name)
        # img.tag(new_docker_img_name, tag= 'latest')




        #print("tagged image: %s and tagged to: %s" % (docker_img_name, new_docker_img_name))
        #logging.info(client.containers.get('kafkamessagetier_zoo1_1').logs().split("\n"))
        # logs
        # for line in client.containers.get(docker_container_name).logs().split("\n"):
        #     if "WARN" in line:
        #         logging.warning(line)
        #     else:
        #         logging.info(line)
        #
        # subprocess.check_output(['docker-compose' ,'stop'])

        #
        # logging.info("removing image %s" % new_docker_img_name)
        # subprocess.check_output(['docker' ,'rmi', new_docker_img_name])
        # logging.info("image %s was removed" % new_docker_img_name )
        # logging.info("removing container %s" % docker_container_name)
        # subprocess.check_output(['docker' ,'rm', docker_container_name])
        print("script exited successfully")
        self.images = []
        #subprocess.check_output(['docker', 'rmi repox:edge-edge'])
        #subprocess.run(['docker', 'images'])
        return

if __name__ == '__main__':

    manager = Manager()
    # manager.get_schedule()
    # manager.get_images()
    # print("Got images; ", manager.images)
    # print("Got teams; ", manager.scheduled_teams)
    while(True):
        manager.start()
        time.sleep(10)
