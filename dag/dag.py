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
from airflow.operators.python_operator import PythonOperator
#from warnings import filterwarnings
#filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

def decode(input_pass):
    message_bytes =input_pass.encode('ascii')
    base64_bytes = base64.b64decode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message
with open('config.json') as f:
    config = json.load(f)
password=decode(config['database']['password'])
password_upt= urllib.parse.quote_plus(password)
db_string = f"postgresql://{config['database']['username']}:{password_upt}@{config['database']['host']}:{config['database']['port']}/{config['database']['database_name']}"
print(db_string)
def database_ingestion():
    try:
        engine = db.create_engine(db_string)
        connection = engine.connect()
        sales_query =  "select * from store_salary;"
        sales_data_df = pd.read_sql_query(sales_query, connection)
        return sales_data_df
    except Exception as e:
        logging.error(f'Error in database_ingestion {e}')
 
def model_selection():
    try:
        logging.basicConfig(level=config['other_configurations']['logging_level'],filename= r'C:\Users\91630\sarima_model.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')
        logger = logging.getLogger(__name__)
        sales_data_df = database_ingestion()
        sales_data_df['totalsal'].fillna(value=sales_data_df['totalsal'].mean(), inplace=True)
        model = auto_arima(sales_data_df['totalsal'], seasonal=True, m=2, trace=True)
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
    except Exception as e:
        logging.error(f'Error training and forecasting sales data: {e}')



if __name__ == "__main__":
     
    default_args = {
        'owner': 'airflow',
        'start_date': datetime(2022, 1, 1),
        'retries': 0,
        'retry_delay': timedelta(minutes=5),
    }
 
    dag = DAG(
    'sales_forecasting_pipeline',
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