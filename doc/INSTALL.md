# Install

1. Clone this project:
    ```bash
    git clone <GIT_URL>
    ```

2. Install python 3.7 64 bit (these instructions might not work with 32 bit). We suggest using a virtual environment if you know how.

3. Install PostgreSQL and create a Database and a User who can access it  
    * If you use Docker, run:
    ```
    docker run --name aiarena-web-postgres -p 5432:5432 -e POSTGRES_PASSWORD=aiarena -d postgres:15.5
    docker exec -i aiarena-web-postgres psql -U postgres -c "create user aiarena with encrypted password 'aiarena' createdb"
    docker exec -i aiarena-web-postgres psql -U postgres -c "create database aiarena with owner aiarena"
    docker exec -i aiarena-web-postgres psql -U postgres -c "grant all privileges on database aiarena to aiarena"
    ```

    * Otherwise, connect to your PostgreSQL installation with `psql -U postgres` and call:
    ```
    create user aiarena with encrypted password 'aiarena' createdb;
    create database aiarena with owner aiarena;
    grant all privileges on database aiarena to aiarena;
    ```

4. Install python modules
    ```
    pip install -r ./requirements.DEVELOPMENT.txt
    ```
   

5. Modify the Website config to use your Database.  
    If you are using a standard postgres setup at localhost:5432 and step 3's SQL script, then you can skip this step -
    the credentials will already be configured.  
    If you need to configure different credentials, make a copy of the `/aiarena/example-dev-env.py` file as 
    `/aiarena/env.py` and update the relevant details

6. Initialize Website DB. Set environment variable `DJANGO_ENVIRONMENT` to `DEVELOPMENT` and then run:
    ```
    python manage.py migrate
    ```

7. Create static files
   ```
   python manage.py collectstatic
   ```

8. Seed the database with data users and match data
    ```
    python manage.py seed
    # Optional
    python manage.py generatestats
    ```

9. (Optional) Configure redis cache.  
   _For most development purposes you can skip this step but note that any components that rely on redis may not work properly._
   
    * If you have Docker installed, it can easily be installed and run. 
        1. Install Redis
           ```
           docker pull redis
           ```
        2. Run Redis, this command uses Docker's port forwarding to let the django server access the container. 
           ```
           docker run --name aiarena-web-redis -p 6379:6379 -d redis
           ```
     * You can also install Redis on your machine by following the instructions [here](https://redis.io/download)


10. Launch the Website then navigate your browser to `http://127.0.0.1:8000/`
    ```
    python manage.py runserver
    ```
    You can log into the website using the accounts below:      
    Admin user: username - devadmin, password - x.  
    Regular user: username - devuser, password - x.


## Configure dev environment

### Install pre-commit hooks

Assuming you have run `pip install -r ./requirements.DEVELOPMENT.txt`, you only need to run this to set up pre-commit linter checking.
```
pre-commit install
```