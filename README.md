# Installation guide

## Requirements
- Ubuntu 22.04
- Docker, Docker-compose

## Install docker.io and docker-compose
```bash
apt update && apt upgrade -y && apt install docker.io docker-compose -y
```

## Clone the repo
```bash
git clone <repo url>
cd <repo dir>
```

## Copy and edit .env file
```bash
cp .env.example .env
nano .env
```

## Start the container
```bash
docker-compose up -d --build
```

# Maintenance guide

## How to reboot the container?
```bash
docker-compose up -d --build
```

## How to get logs
```bash
docker-compose logs
# or
docker logs <container name>
```

## How to stop the container
```bash
docker-compose stop
```