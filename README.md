# flask-microservices
Test Application based on Python Flask and Docker

###### To access database
$ docker exec -ti users-db psql -U postgres -W

###### To build the docker compose
$ docker-compose build

###### To run the docker images
$ docker-compose up -d

###### To start/stop docker machine
$ docker-machine stop default
$ docker-machine start default

###### To list docker processes
$ docker ps

###### to remove docker image
$ docker rmi image

###### to remove stopped container
$ docker rm -f $(docker ps -a -q)

###### to remove all dangling images
$ docker rmi $(docker images -f "dangling=true" -q)

###### to setup database for the first time
$ docker-compose run users-service python manage.py recreate_db

$ docker-compose run users-service python manage.py seed_db

###### to run tests
$ docker-compose run users-service python manage.py test 