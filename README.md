#  A sales forecasting pipeline using Apache Airflow 
## Steps to install docker 
Download the Docker Desktop installer for Windows from the Docker website (https://www.docker.com/get-started).

To finish the installation, run the installer and follow the on-screen instructions.

Docker should start automatically after installation. You can confirm this by looking in the system tray for the Docker icon.

Open a command prompt or PowerShell window and type docker --version to test your installation. This should show the Docker version you installed.

## After installing the docker write a docker-compose.yml file
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
 Python modules have been included in the image built from the Dockerfile. This would ensure that the sales.py program can be run in a container based on that image without encountering any missing module errors.
 The modules which are required to run the sales.py are
 
 FROM puckel/docker-airflow:1.10.9
 
 RUN pip install requests
 
 RUN pip install pandas
 
 Run pip install sqlalchemy
 
 Run pip install numpy
 
 Run pip install pmdarima
 
 Run pip install apache-airflow 
 
 



## How to run the Apache-airflow dag

### get into projects folder and run 
docker-compose up -- build

The command docker-compose up --build starts the containers defined in the docker-compose.yml file and rebuilds if necessary. 


The postgres container will be started first, followed by the webserver container.

The Dockerfile specified in the webserver service's build section will be used to build the webserver container.

The webserver container will be configured with the environment variables, volumes, ports, and command specified in the webserver service.

Once both containers are running, To access the Airflow webserver, navigate to http://localhost:8080 in the web browser.














