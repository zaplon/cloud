#!/usr/bin/env bash
docker build . -f docker/web/Dockerfile -t docker.io/zaplon/gabinet_prod:latest
docker push docker.io/zaplon/gabinet_prod:latest