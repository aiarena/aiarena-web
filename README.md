# aiarena-web
A website for running the aiarena.net infrastructure.

## Dev setup

1. Clone the project

    You can use the IDE way of doing it, or do it manually:
    
    ```shell
    git clone https://github.com/aiarena/aiarena-web/
    ```

2. [Make sure](https://docs.astral.sh/uv/getting-started/installation/) you have `uv` installed

3. Set up your virtual environment
    
    In Pycharm, you just need to create a new local interpreter (make sure to select `uv` as the interpreter type and match the python version to the one currently set in [pyproject.toml](./pyproject.toml)). Otherwise, you can do:

    ```shell
    uv venv
    ```
   
    After this is done, you'll want to run

    ```shell
    uv sync
    ```

    to install python deps, and

    ```shell
    cd aiarena/frontend-spa && npm install
    ```
   
    to install javascript deps.

4. Configuring environment variables

    You'll want to set environment variable `DJANGO_ENVIRONMENT` to `DEVELOPMENT`. 
    There are several ways to do this - one way is to prefix every command with the variable:
    `DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py runserver`
    
5. Set up Postgres and Redis

    There is a [docker-compose.yml](./docker-compose.yml) file that's configured to run correct versions of Postgres and Redis. It already ensures that there is a correct user / database created in the Postgres DB. If you want to manually connect to those, look up the credentials in the compose file.

    <br />

    The `DATABASES` setting and Redis-related settings in [default.py](./aiarena/settings/default.py) will automatically point to those databases, but if you wish to use a custom database config, you can override those settings in [local.py](./aiarena/settings/local.py). This file is gitignored.

    <br />
   
    For Pycharm users, there's a ready-made `Databases` run config that launches the docker-compose file, as well as a `Project` compound run config that launches everything needed for development.

6. Populate the DB

    You can go two routes here - either populate it with seed data (if you don't want to worry about protecting production data on a local machine, or don't have access to AWS), or just restore the production backup locally (better for reproducing performance issues, simpler, but requires AWS access).

    * Seed data - run `uv run manage.py migrate` to apply the database migrations, then `uv run manage.py seed` and optionally `uv run manage.py generatestats`
    * Restore backup - run `uv run run.py restore-backup --s3`. That will download the latest production backup, which will already have the migrations applied.

7. Launching the Website


    If the enviornment is not activated - activate it: 
    ```shell
    source .venv/bin/activate
    ```




    In the terminal, run: 
    
    ```shell
    docker compose up
    ```

    In another terminal run:

    ```shell
    uv run manage.py graphql_schema
    uv run manage.py runserver
    ```

    In another terminal - navigate to aiarena-web/aiarena/frontend-spa 
    ```shell 
    cd aiarena/frontend-spa
    ```
    then run:
    ```shell
    npm run start_relay
    ```    
    In yet another terminal - navigate to aiarena-web/aiarena/frontend-spa
    ```shell 
    cd aiarena/frontend-spa
    ```
    then run:
    ```shell
    npm run dev
    ```    
    
    AI Arena should now be available in your browser at `http://127.0.0.1:8000/`
    If you used seed data in the previous step, you can log into the website using the accounts below:      
    Admin user: username - devadmin, password - x.  
    Regular user: username - devuser1, password - x.
        
    <br />

    Otherwise (if you restored the production backup), you can log in with the same username and password that you use in aiarena.net.

8. Install pre-commit hooks

    Whenever you're pushing code to production, we'll run linters and make sure your code is well-formatted. To get faster feedback on this, you can install pre-commit hooks that will run the exact same checks when you're trying to commit.

    ```shell
    uv run pre-commit install
    ```

## Setting VS code enviornment variables:

    After creating the venv with UV. navigate to ./venv/bin/activate and add the env export just before "deactivate()":
    ```shell
    export DJANGO_ENVIRONMENT=DEVELOPMENT
    ```
    Then reactivate the environment with source.

### Set up AWS access

This is needed to restore production backups, or do any other work with production environment.

1. Make sure you have an AWS user with `SuperPowerUsers` group
2. Configure your AWS credentials:

    Get your `Access key ID` and `Secret access key` in `IAM` section of
    AWS Console and save them on your machine under `aiarena` profile:
    - go to https://315513665747.signin.aws.amazon.com/console
    - in the [IAM](https://console.aws.amazon.com/iam/) find your user, go to `Security credentials` and create an access key if you don't have one
    - use the credentials to configure AWS:

    ```sh
    $ aws configure --profile aiarena
    AWS Access Key ID [None]: ******
    AWS Secret Access Key [None]: ******
    Default region name [None]: eu-central-1
    Default output format [None]:
    ```

### HOWTO: Run commands in production

Pre-requisites: 

1. Install local development tools and configure your AWS credentials, as 
   described above;
2. Install [AWS Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

After that you should be able to use the `uv run.py production-one-off-task` command.

It will spin up a new task with no production traffic routed to it, and with custom CPU and memory values. 

By default, the task will be killed in 24 hours to make sure it's not consuming money after it's finished. You can use the `--lifetime-hours` flag to override this behaviour if you need to run something really long.

Also, by default, the task is killed early if you disconnect from the ssh session. Use the `--dont-kill-on-disconnect` flag to disable this behaviour, if you want it running in the background.

### HOWTO: Connect to production containers for debugging

Pre-requisites: 

1. Install local development tools and configure your AWS credentials, as 
   described above;
2. Install [AWS Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

After that you should be able to use the `uv run.py production-attach-to-task` command. It will help you find an existing production container, and connect you to it.

You can also specify a task ID with `--task-id <task id here>` flag, if you already have one (for example, if you created a one-off task).


### HOWTO: Update the CloudFormation stack

This is the way we do Infrastructure-as-Code. All the AWS resources we have are in `index-default.yaml` template file. Make some changes to it, and then generate a CloudFormation template based on it:

```
uv run.py cloudformation
```

The template would be saved to `cloudformation-default.yaml` in the project root
directory. Next, use this template to update the stack in `CloudFormation`
section of AWS Console:

1. Select `aiarena` and click `Update`
2. Choose `Replace current template`
3. Choose `Upload a template file`, and select the `cloudformation-default.yaml` file that you generated in the previous step. Then click next.
4. Update the variables if you want to, then click next until you get to the last screen.
5. On the last screen please wait for the `Change set preview` to be generated, it can take a minute. Take a look at the preview, and make sure it makes sense.
6. Click `Submit` and watch the infrastructure change


## How does the deployment work?

We're running the application code inside of Fargate containers, so to deploy a new version to prod, we need to build a new Docker image, and then update the Fargate containers to use it.

Here's how the deployment process works:
1. Changes are pushed to the `main` branch
2. GitHub Actions starts running tests/linters and in parallel runs `uv run.py prepare-images`, which builds an image and pushes it to Elastic Container Registry with a tag like `build-111-amd64`
3. If all tests/linters passed, `uv run.py ecs` runs next:
   1. It makes a `latest` alias to the image that we built earlier
   2. Then, it runs `manage.py migrate`
   3. Finally, it triggers a rolling update to all the Fargate containers, that will use the `latest` image
4. As a final step, `uv run.py monitor-ecs` runs. It watches the rolling update, and makes sure all the services are replaced, and running. This step can fail if the containers are failing to start for some reason.

## License

Licensed under the [GPLv3 license](LICENSE).