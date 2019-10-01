docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker-remove-all-pycharm-helper

