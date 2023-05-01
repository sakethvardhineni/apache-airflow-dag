#  A sales forecasting pipeline using Apache Airflow 
## steps to install docker 
Download the Docker Desktop installer for Windows from the Docker website (https://www.docker.com/get-started).
To finish the installation, run the installer and follow the on-screen instructions.
Docker should start automatically after installation. You can confirm this by looking in the system tray for the Docker icon.
Open a command prompt or PowerShell window and type docker --version to test your installation. This should show the Docker version you installed.

##After installing the docker write a decker-compose.yml file
The file's version number begins with 3.7.
The file defines two services: postgres and webserver.
The postgres service loads the official postgres image version 9.6 and configures the database's environment variables.
A Dockerfile in the./dockerfiles directory is used to build the webserver service.
Because the webserver service is dependent on the postgres service, the postgres service will be started before the webserver service.
The webserver service configures the Airflow webserver's environment variables and exposes the Airflow webserver's default port (8080) to the host machine.
The volumes section mounts the host machine's./dags directory to the container's /usr/local/airflow/dags directory.






## get into projects folder and run 
docker-compose up -- build


