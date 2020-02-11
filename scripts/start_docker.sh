docker stop containername
docker rm containername

cd /srv/dlc-shared/Docker4DeepLabCut2.0
GPU=0 bash ./dlc-docker run -d -p 2351:8888 -e USER_HOME=$HOME/projects-dlc/ --name containername mydlcuser:mydlcdocker
docker exec --user $USER -it containername /bin/bash
