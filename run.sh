#!/usr/bin/bash

name=flask-userapp
docker build -t $name .
docker stop $name || true
docker rm $name || true
docker run -d --name $name --net postgres -p 5000:5000 $name

