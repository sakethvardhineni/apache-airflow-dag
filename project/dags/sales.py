import json
import logging
import pandas as pd
from pmdarima.arima import auto_arima
import sqlalchemy as db
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import base64
import urllib
from airflow import DAG
from datetime import timedelta, datetime
import os

from airflow.operators.python_operator import PythonOperator




def decode(input_pass):
    message_bytes =input_pass.encode('ascii')
    base64_bytes = base64.b64decode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message
basedirectory=os.getcwd()
config_path=os.path.join(basedirectory,"dags/config.json")
sirma_path=os.path.join(basedirectory,"dags/sarima_model.log")
sales_data_file = os.path.join(basedirectory,"dags/store_sales.csv")
with open(config_path) as f:
    config = json.load(f)
#password=decode(config['database']['password'])
#password_upt= urllib.parse.quote_plus(password)
db_string = f"postgresql://{config['database']['username']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database_name']}"


def inject_data_db():
    try:
        engine = db.create_engine(db_string)
        connection = engine.connect()
        sales_data = pd.read_csv(sales_data_file)
        sales_data.to_sql('store_salary',connection, if_exists='append', index=False)
    except Exception as e:
        logging.error(f'Error in database_ingestion {e}')
 
inject_data_db()

def database_ingestion():
    try:
        engine = db.create_engine(db_string)
        connection = engine.connect()
        sales_query =  f"SELECT * FROM {config['database']['sales_tablename']};"
        sales_data_df = pd.read_sql_query(sales_query, connection)
        return sales_data_df
    except Exception as e:
        logging.error(f'Error in database_ingestion {e}')
 
def model_selection():
    try:
        logging.basicConfig(level=config['other_configurations']['logging_level'],filename= r'./ssarima_model.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')
        logger = logging.getLogger(__name__)
        sales_data_df = database_ingestion()
        sales_data_df['totalsal'].fillna(value=sales_data_df['totalsal'].mean(), inplace=True)
        model = auto_arima(sales_data_df['totalsal'], seasonal=True, m=12, trace=True)
        logger.info('Selected SARIMA model parameters:')
        logger.info(f'p: {model.order[0]}, d: {model.order[1]}, q: {model.order[2]}')
        logger.info(f'P: {model.seasonal_order[0]}, D: {model.seasonal_order[1]}, Q: {model.seasonal_order[2]}, m: {model.seasonal_order[3]}')
        return model
    except Exception as e:
        logging.error(f'Error in model_selection {e}')
         
 
def model_training_and_forecasting():
    try:
        sales_data = database_ingestion()
        model = model_selection()
        engine = db.create_engine(db_string)
        connection = engine.connect()
        sarima_model = ARIMA(sales_data['totalsal'], order=model.order, seasonal_order=model.seasonal_order,enforce_stationarity=False)
        sarima_model_fit = sarima_model.fit()
        forecast = sarima_model_fit.forecast(steps=30)
        forecast_data = pd.DataFrame({'belongs_to': pd.date_range(start=sales_data['belongs_to'].max()+pd.Timedelta(days=1), periods=30),
                                     'totalsal': forecast})
        forecast_data.to_sql('forecast', connection, if_exists='append', index=False)
        sales_query =  "select * from forecast;"

        sales_data_dfresult = pd.read_sql_query(sales_query, connection)
        logging.info(f'forecate result =\n{sales_data_dfresult}')
    except Exception as e:
        logging.error(f'Error training and forecasting sales data: {e}')

    
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
