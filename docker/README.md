# Docker compose usage


## Seed the app with data

```shell
cd docker/local/
docker-compose run aiarena-web python3 manage.py seed

# OR

docker-compose -f docker/local/docker-compose.yml run aiarena-web python3 manage.py seed
```

## Run aiarena-web app
```shell
cd docker/local/
docker-compose up aiarena-web  

# OR

docker-compose -f docker/local/docker-compose.yml up aiarena-web
```

## Stop aiarena-web app
```shell
cd docker/local/
docker-compose down

# OR

docker-compose -f docker/local/docker-compose.yml down
```

## Run the tests

```shell
cd docker/local/
docker-compose up aiarena-web-test

# OR

docker-compose -f docker/local/docker-compose.yml up aiarena-web-test
```