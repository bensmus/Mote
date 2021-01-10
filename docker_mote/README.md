# Docker mote

*This directory has source files to run the bot using Docker containers.*

If we want to run the bot on our Raspberry Pi, we can use Docker to avoid installing a bunch of large python modules on our system. Another advantage of using Docker as opposed to just running the python program and the redis server is that we can easily see the states of our system, for example with `docker ps -a`. It's more organized. Finally, Docker containers can be set to restart automatically if your Pi restarts.

## Steps to setup bot to be hosted on Raspberry Pi with docker

1. Make a directory on your Pi that has 
    - .env file for Redis server password and Discord bot token
    - Dockerfile
    - requirements.txt
    - mote.py

2. Install docker onto your Raspberry Pi.
Here's a good tutorial for that: https://phoenixnap.com/kb/docker-on-raspberry-pi 


3. The idea is to have two docker containers, one running as a redis server, and one running as a redis client and as a discord client (the python script). Since the redis client container has to communicate with the redis server container, we make a user defined network (one of the great features of docker, I guess!) which both containers will be a part of. 
```
docker network create net0
```

4. Start the redis container with the password in the .env file replacing "password" in this command. Call the container redis_container.
 ```
docker run -d \
	-p=6379:6379 \
	-v=redis_persistence:/usr/src/app \
	--restart unless-stopped \
	--name redis_container \
	--network net0 \
	redis \
	redis-server \
	--appendonly yes \
	--requirepass "password" 
```

5. Start the python container. Since we have some custom code that we wrote for the bot (all the bot stuff!) we need to first build a docker image. The proccess makes use of all the files in the directory, and relies on the Dockerfile for instructions. 

Building the docker image:
```
docker build -t mote .
```

Starting the container based on this image:
```
docker run -d \ 
	--restart unless-stopped \
	--name mote_container \
	--env-file .env \
	--network net0 \
	mote
```


Yay! There should now be two Docker containers up and running, and the bot should be operational without you having to worry about your credit card getting charged because Heroku pulls a sneaky on you!




