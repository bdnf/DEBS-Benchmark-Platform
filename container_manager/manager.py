import docker
import logging
import subprocess
import datetime
import sys, os
import yaml
import json
import re
from collections import OrderedDict


class Manager:

    def __init__(self):

        LOG_FOLDER_NAME = "manager_logs"
        if not os.path.exists(LOG_FOLDER_NAME):
            os.makedirs(LOG_FOLDER_NAME)
        logging.basicConfig(filename=LOG_FOLDER_NAME+'/compose_manager.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
        self.client = docker.from_env()

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


    def read_yml(self, name, file_number, image, container):
        logging.info("called def read_yml with ix %s, image: %s, container: %s " % (file_number, image, container))
        with open(name) as f:
            list_doc = yaml.safe_load(f)
        list_doc["services"]["client"]["image"] = image
        list_doc["services"]["client"]["container_name"] = container
        volumes = list_doc["services"]["server"]["volumes"]
        log_volume = volumes[1].split(":")
        print("LV", log_volume)
        try:
            log_volume = log_volume[0]+ "/" + str(image.split("/")[1]) +":"+log_volume[1]
        except IndexError:
            log_volume = log_volume[0]+ "/" + str(image.split("/")[0]) +":"+log_volume[1]
        new_volumes = [volumes[0],log_volume]
        print("NW", new_volumes)
        list_doc["services"]["server"]["volumes"] = new_volumes

        split_name = name.split('.')
        new_name = "docker-compose.yml" #str(split_name[0]) + str(file_number) + "."+ str(split_name[1])

        with open(new_name, "w") as f:
            yaml.dump(list_doc, f, default_flow_style=False)
        logging.info("docker compose file saved with name %s" % new_name)
        #return new_name


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

        print(subprocess.check_output(['docker', 'version']))

        teams_file ='teams.txt'
        repo_list = self.grab_teams(teams_file)
        repo_list = OrderedDict(sorted(repo_list.items()))
        print("Teams: ", repo_list)
        print("Tags: ", repo_list.values())



        # client.images.pull('alpine')
        #
        # client.containers.list()

        docker_server_img_name = "benchmark-server"
        docker_container_name = "benchmark-server-logging"
        client_container_name = "client-app-"

        try:
            subprocess.check_output(['docker', 'rm', docker_container_name])
        except Exception as e:
            logging.warning("Container probably not exist yet %s" % e)
            pass

        for ix, docker_img_name in enumerate(repo_list.keys()):
            docker_img_name = str(docker_img_name)
            print("tring with this name: ", docker_img_name)
            try:
                subprocess.check_output(['docker', 'rm', docker_img_name])
            except Exception as e:
                print(e)
            try:
                print("Pulling image %s" % docker_img_name)
                self.client.images.pull(docker_img_name)
                tag = subprocess.check_output(['docker', 'inspect', docker_img_name])
                tag = json.loads(tag.decode('utf-8'))[0]["Id"]
                print(tag)
                if repo_list[docker_img_name] != tag:
                    repo_list[docker_img_name] = tag
                    print(repo_list)
                    with open(teams_file.split('.')[0]+'.json', 'w') as outfile:
                        json.dump(repo_list, outfile)
                    logging.info("pulled image: %s" % docker_img_name)
            except Exception as e:
                logging.error("Error during pull happened %s" % e)
                print("Probably can't access image: %s. Error %s" % (docker_img_name, e))
                continue
            new_img_name = docker_img_name.split("/")[1]# +"-"+ str(ix)
            try:
                img = self.client.images.get(docker_img_name)
            except docker.errors.ImageNotFound as e:
                logging.error("Error during pull happened %s" % e)

            img.tag(new_img_name, tag= 'latest')
            logging.info("tagged image: %s and tagged to: %s" % (docker_img_name, new_img_name))
            subprocess.check_output(['docker' ,'rmi', docker_img_name])
            logging.info("untagged old image %s" % docker_img_name)
            new_container_name = docker_container_name + str(ix)
            # print("Current dir is %s " % os.getcwd())
            file = "docker-compose-mock.yml"
            self.read_yml(file, ix, new_img_name, client_container_name+docker_img_name.split("/")[1]) #TODO change for [0] for client repo name
            logging.info("calling docker-compose -f  up ")

            # subprocess.check_output(['docker-compose' ,'up', '-d', '--build'])
            #subprocess.check_output(['docker-compose', 'up', '--build', '--abort-on-container-exit'])
            # = subprocess.Popen(,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cmd = ['docker-compose', 'up', '--build', '--abort-on-container-exit']
            for path in self.execute(cmd):
                print(path, "")
                logging.info(path)


            logging.info("docker-compose -f %s exited")
            #subprocess.check_output(['docker' ,'rm', client_container_name+str(ix)])


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
        logging.info("script exited successfully")
        #subprocess.check_output(['docker', 'rmi repox:edge-edge'])
        #subprocess.run(['docker', 'images'])
        return

if __name__ == '__main__':

    manager = Manager()
    manager.start()
