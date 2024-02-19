# Devcontainers : Local Development to EC2 Deployment Workflow

## Overview

This project demonstrates the use of GitHub Actions in the context of local development with devcontainers. It features a Docker Compose setup, a Dockerfile with Flask app files, and a workflow for building and pushing the Docker image to Docker Hub. The workflow also updates a container on an EC2 instance.

The services used consist of a postgres container and a flask api with some endpoints. At laucnh, the python container populates the Database and starts the api on port 5000.

It is a basic set up to experiment with containerized local development environment and CI/CD workflows.

## Prerequisites

Before getting started, ensure you have the following:

- Docker and Docker Compose installed on your machine
- A GitHub repository for your project
- An AWS account and the ability to launch a basic EC2 instance
- VS Code installed on your machine with the Docker and Dev Containers extensions

## Setting Up a Containerized Local Development Environment

Use the `sample_docker-compose.yml` example to create a Docker Compose configuration that you will use to launch your local development environment with the help of the Dev Containers VS Code extension. (It will also help you in a later when deploying your instance on EC2).

This setup will enable you to develop directly inside the container while seamlessly syncing changes between your local files and those inside the container.

```yml
...

  flask-api:
    build: .
    container_name: flask-api
    volumes:
      - ./:/app # Sync local directory with container
    ports:
      - "5000:5000"
      - "8443:443"
    depends_on:
      - pg-db-ws5
    networks:
      datastats:
        ipv4_address: 172.20.0.3

...
```
In this example we want to be able to interactively update the flask-api container via VS Code. Make sure to map your local directory to the working directory of the container in the `volumes` configuration.

1. clone this repo 
```bash
git clone https://github.com/caidam/devcontainer-workflow.git
```

2. Create your **local** `docker-compose.yml` (you can use the model `sample_local_docker-compose.yml` provided in the repo) 

3. Create a **local** `.env` file to assign the environment variables for the project (you can also use the model `sample.env` provided in the repo)

> Make sure to add the .env files to your `.gitignore` since it is not meant to be pushed on GitHub.

4. Launch the containers with the command `docker-compose up -d`

5. `Attach` to the desired container using the Dev Containers extension (in our case `flask-api`)

6. Build and push your `flask-api` image to Docker Hub :

```bash
docker login -u <username>
docker build -t <image_name> .
docker tag <image_name> <username>/<image_name>
docker push <username>/<image_name>
``` 

At this point your local environment is set up and you should be able to interactively modify your container with VS Code. Your local project directory and the container's files are synchronized, you can test it to make sure it works fine.

## Deploying The Services on EC2

To set up the workflow, we first want to manually deploy our services on an EC2 instance.

1. Launch a basic ubuntu instance (The free tier will do) and make sure you have the related `Private Key` at your disposal

2. Connect to your instance and enter the below commands :

```bash
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install git -y
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo apt-get install docker-compose -y
mkdir app
cd app
```

3. Inside your newly created app folder copy the content of the `sample_local_docker-compose.yml` file in a file called `docker-compose.yml` on the instance

4. Then copy the content of the updated `sample.env` file in a `.env` file on the instance

5. launch your services :
```bash
sudo docker build -t flask-api . && sudo docker-compose up -d
```

These commands update the system, make the necessary installations and launch the containers.

6. Open the `port 5000` of your instance via Security Groups and try the app's endpoints

You can also connect to the instance and manually check that the containers are running using `docker ps`

## Creating a CI/CD Workflow with Github Actions

- Our local environment is set up.
- Our containers are deployed on the cloud.

Now we will use Github Actions to create a workflow that will give a us way to easily update our API app when needed.

1. Configure project's Secrets on the GitHub website

This tedious step consists of copying and pasting your environment variables on Git Hub since your `.env` file will not be pushed to the repo.

> Alternatively you can install the `GitHub Actions` extension on VS Code to complete this step a bit quicker

2. Add your Docker Hub credentials to the Secrets

- `DOCKER_HUB_USERNAME` : your username
- `DOCKER_HUB_ACCESS_TOKEN` : an access token you can easily generate via Docker Hub

3. Add your instance's credentials to the Secrets

The expected credentials are : 

- `EC2_HOST` : the public ip or dns of your instance
- `EC2_USERNAME` : it is `ubuntu` by default, you can see it in the "Connect to instance" menu 
- `EC2_SSH_KEY` : your private key (.pem), open it with VS CODE and copy/paste the entirety of the file.

4. Check the workflow is well configured

Double check the environment variables and configurations.

> In the last commands of the `.github/workflows/push-docker-ec2-workflow.yml` file, make sure to use the correct directory name :

```yml
    steps:
      - name: Execute remote SSH commands to update Docker container
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd app &&
            sudo docker-compose stop flask-api &&
            sudo docker-compose rm -f flask-api &&
            sudo docker rmi ${{ secrets.DOCKER_HUB_USERNAME }}/flask-api &&
            sudo docker-compose up -d flask-api
```

> The command `cd app &&` should match the path of your project folder on EC2.

5. Customize the workflow to your liking

As it is the workflow consists of two jobs :

- Job 1 builds and pushes a new version of the `flask-api` image to Docker Hub.

- Job 2 updates the `flask-api` container on the EC2 instance

The workflow is triggered each time a commit is pushed to the main branch with the code "push-image" in the commmit message.

For example, the below commands would trigger the workflow :

```bash 
git add .
git commit -m "updated api endpoint push-image"
git push -u origin main
```

And the below would not :

```bash
git add .
git commit -m "updated README"
git push -u origin main
```

6. Test the Workflow

Push some visible changes to your endpoints and make sure they have been applied in your instance after making sure the workflow is done running.

> On your machine you can connect and push to github from inside the container (but you will need to install git and authentify) or choose to do it locally. 

> When modifying files make sure to double check if you are working from inside the container or locally. Since the file are synched, version issues can arise if you are modifying both sides in parallel.

## Troubleshooting and Cleaning

### Troubleshooting

If you encounter issues, performing the following sanity check may help :

- Double check your instance's Security Group inbound rules and make sure to open port 5000
- Check the logs of your containers locally or on the instance with the command `docker logs container-name`
- Check the logs of the Git Hub Actions Workflow when it's done running

### Cleaning

After you're done experimenting make sure to terminate your instance and free up local memory by deleting your unused containers, images, volumes and networks :

- remove all stopped containers : `docker container prune`
- delete unused images : `docker image prune`
- remove all images not associated with a container : `docker image prune -a`
- delete unused volumes : `docker volume prune` 
- delete unused networks : `docker network prune`
- delete all unused resources : `docker system prune -a`