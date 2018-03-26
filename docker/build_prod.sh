#!/usr/bin/env bash
docker build docker/web -t docker.io/zaplon/gabinet_prod:latest
docker push docker.io/zaplon/gabinet_prod:latest