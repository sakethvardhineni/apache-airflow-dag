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

### Get into projects folder and run 
docker-compose up -- build

The command docker-compose up --build starts the containers defined in the docker-compose.yml file and rebuilds if necessary. 


The postgres container will be started first, followed by the webserver container.

The Dockerfile specified in the webserver service's build section will be used to build the webserver container.

The webserver container will be configured with the environment variables, volumes, ports, and command specified in the webserver service.

Once both containers are running, To access the Airflow webserver, navigate to http://localhost:8080 in the web browser.

## After accesing the http://localhost:8080 the Airflow page looks like 

![image](https://user-images.githubusercontent.com/132186396/235391228-3c2b3c6c-47c1-4d79-a73f-efd56985a8e6.png)

In Apache Airflow, a DAG (Directed Acyclic Graph) is a collection of tasks that are organized in a way that reflects their relationships and dependencies. Each DAG represents a workflow that needs to be executed, and it defines the order in which the tasks should be run.

## There are three tasks which will run in the folloing order

### First is database_ingestion 
    
 where we Create a database engine object using a db_string which is of the format  f"postgresql://{config['database']['username']}:{password_upt}@{config['database']['host']}:{config['database']['port']}/{config['database']['database_name']}" 
    
Establish a connection to the database using the engine object

Execute a SQL query called sales_query to retrieve all data from a table called store_salary

Load the data into a Pandas DataFrame called sales_data_df

If any error occurs during this process, the function will log the error message using the Python logging module.
### Second is modelselection 
 The logging.basicConfig() method is used to set up logging for the script, with the logging level and log file location specified in the configuration             dictionary.
 
 The missing values in the totalsal column of the DataFrame are filled with the mean value of the column using the fillna() method.
 
  The auto_arima() function from the pmdarima library is used to automatically select the best parameters for the SARIMA model based on the sales data.
  
  The selected model parameters are logged using the logger.info() method.
     
### Third is model_training_and_forecasting
An ARIMA object is created with the sales data and the best parameters selected by the model_selection() function.
      
 The fit() method is called on the ARIMA object to fit the model to the sales data.
     
The forecast() method is called on the fit() object to forecast future sales for the next 30 time steps.

The forecasted sales data is stored in a DataFrame with the dates as the index and the forecasted sales as the only column.


The forecast_data DataFrame is written to the forecast table in the database using the to_sql() method with if_exists='append' to add the new data to the          table without overwriting existing data.

Any errors that occur during the execution of this function are logged using the logging.error() method with a message that includes the specific error that      occurred.


## The code for DAG
```
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 4, 30),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
'sales',
default_args=default_args,
description='A DAG to automate sales forecasting using SARIMA model',
schedule_interval='@daily',
catchup=False
)
task_read_sales_data = PythonOperator(
    task_id='read_sales_data',
    python_callable=database_ingestion,
    dag=dag
)

task_select_model_parameters = PythonOperator(
    task_id='select_model_parameters',
    python_callable=model_selection,
    dag=dag
)

task_train_and_forecast = PythonOperator(
    task_id='train_and_forecast',
    python_callable=model_training_and_forecasting,
    dag= dag
)

task_read_sales_data >> task_select_model_parameters  >> task_train_and_forecast
```

The code defines a DAG named "sales" with default arguments and a daily schedule. The DAG has three tasks defined as PythonOperators, each with a task_id and python_callable:

The first task, task_read_sales_data, executes the Python function database_ingestion, which retrieves sales data from a database and returns it as a Pandas DataFrame.

The second task called task_select_model_parameters runs a Python function model_selection which selects the best parameters for a SARIMA (Seasonal Autoregressive Integrated Moving Average) model based on the sales data.

The third task called task_train_and_forecast runs a Python function model_training_and_forecasting which trains the SARIMA model with the selected parameters on the sales data and produces sales forecasts.

The tasks are ordered using the '>>' so that "task_read_sales_data" is executed before "task_select_model_parameters", and "task_select_model_parameters" is executed before "task_train_and_forecast". The DAG is designed to run without catching up on missed runs.
     
  ## After  Apache airflow gets triggered it  looks like 
  
  ![image](https://user-images.githubusercontent.com/132186396/235392806-71a093bd-ee1b-40b7-90bc-07959f62bf72.png)
  
  
 Where the borders of the DAG is green which indicate the runnning status is success.
     

A DAG is defined as a Python script that contains a set of tasks, each represented by a Python operator. The tasks are arranged in a way that reflects their dependencies, with arrows indicating the direction of data flow.














