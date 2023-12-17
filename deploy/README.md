## Prerequisites for working with infrastructure

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

### How does the deployment work?

We're running the application code inside of Fargate containers, so to deploy a new version to prod, we need to build a new Docker image, and then update the Fargate containers to use it.

Here's how the deployment process works:
1. Chagnes are pushed to the `main` branch
2. GitHub Actions starts running tests/linters and in parallel runs `run.py prepare-images`, which builds an image and pushes it to Elastic Container Registry with a tag like `build-111-amd64`
3. If all tests/linters passed, `run.py ecs` runs next:
   1. It makes a `latest` alias to the image that we built earlier
   2. Then, it runs `manage.py migrate`
   3. Finally, it triggers a rolling update to all the Fargate containers, that will use the `latest` image
4. As a final step, `run.py monitor-ecs` runs. It watches the rolling update, and makes sure all the services are replaced, and running. This step can fail if the containers are failing to start for some reason.


### HOWTO: Run commands in production

Pre-requisites: 

1. Install local development tools and configure your AWS credentials, as 
   described above;
2. Install [AWS Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

After that you should be able to use the `python3 run.py production-one-off-task` command.

It will spin up a new task with no production traffic routed to it, and with custom CPU and memory values. 

By default, the task will be killed in 24 hours to make sure it's not consuming money after it's finished. You can use the `--lifetime-hours` flag to override this behaviour if you need to run something really long.

Also, by default, the task is killed early if you disconnect from the ssh session. Use the `--dont-kill-on-disconnect` flag to disable this behaviour, if you want it running in the background.

### HOWTO: Connect to production containers for debugging

Pre-requisites: 

1. Install local development tools and configure your AWS credentials, as 
   described above;
2. Install [AWS Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

After that you should be able to use the `python3 run.py production-attach-to-task` command. It will help you find an existing production container, and connect you to it.

You can also specify a task ID with `--task-id <task id here>` flag, if you already have one (for example, if you created a one-off task).


### HOWTO: Update the CloudFormation stack

This is the way we do Infrastructure-as-Code. All the AWS resources we have are in `index-default.yaml` template file. Make some changes to it, and then generate a CloudFormation template based on it:

```
python3 run.py cloudformation
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