#  A sales forecasting pipeline using Apache Airflow 
## steps to install docker 
Download the Docker Desktop installer for Windows from the Docker website (https://www.docker.com/get-started).

To finish the installation, run the installer and follow the on-screen instructions.
Docker should start automatically after installation. You can confirm this by looking in the system tray for the Docker icon.
Open a command prompt or PowerShell window and type docker --version to test your installation. This should show the Docker version you installed.

## After installing the docker write a decker-compose.yml file
the version of the python is  3.7.

defined two services: postgres and webserver.

The postgres service loads the official postgres image version 9.6 and configures the database's environment variables.

A Dockerfile in the./dockerfiles directory is used to build the webserver service.
In the Dockerfile i have imported the modules which are required to run the sales.py python program

Because the webserver service is dependent on the postgres service, the postgres service will be started before the webserver service.

The webserver service configures the Airflow webserver's environment variables and exposes the Airflow webserver's default port (8080) to the host machine.

The volumes section mounts the host machine's./dags directory to the container's /usr/local/airflow/dags directory.

The command section specifies the command to run when the container starts up. In this case, it starts the Airflow webserver.

The healthcheck section specifies a health check for the webserver container. It checks whether the Airflow webserver is running by looking for the existence of the airflow-webserver.pid file in the container. If the file exists, the health check passes. The health check runs every 30 seconds and times out after 30 seconds. If the health check fails 3 times in a row, the container will be considered unhealthy.

## Dockerfile
In the Dockerfile i have imported the modules which are required to run the sales.py python program




## get into projects folder and run 
docker-compose up -- build


