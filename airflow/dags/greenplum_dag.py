# INFO STR
import datetime

import pandas as pd

from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.postgres_operator import PostgresOperator



SQL_STR_DICT: dict = dict({
    "CREATE_TABLE_STR" :\
        """
        drop table if exists raw.mock_data;
        
        create table raw.mock_data(
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            gender VARCHAR(255) NOT NULL,
            ip_address VARCHAR(255) NOT NULL
        );
        """,
    "CREATE_TABLE_STR_PD" :\
        """
        drop table if exists raw.mock_data_pandas;
        
        create table raw.mock_data_pandas(
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            gender VARCHAR(255) NOT NULL,
            ip_address VARCHAR(255) NOT NULL,
            report_date VARCHAR(255) NOT NULL
        );
        """,
    "CHECK_RAW_SCHEMA_STR" : "SELECT * FROM pg_catalog.pg_namespace;",
    "CREATE_SCHEMA_STR" : "CREATE SCHEMA raw;",
    "SELECT_TABLES_FROM_RAW" : "SELECT table_name  FROM information_schema.tables WHERE table_schema = 'raw';",
    "SELECT_COLUMN_NAMES" : "SELECT column_name FROM information_schema.columns WHERE table_name = 'mock_data' and table_schema  = 'public';",
})


default_args: dict = dict({
    'owner' : 'airflow',
    'depend_on_past' : False,
    'start_date' : datetime.datetime(2023, 8, 1),
})


def _get_data_and_add_to_raw() -> None:
    pg_hook = PostgresHook(postgres_conn_id = 'greenplum')
    connection = pg_hook.get_conn()
    with connection.cursor() as cursor:
        INSERT_QUERY_STR: str = "INSERT INTO raw.mock_data SELECT * FROM public.mock_data;"    
        cursor.execute(INSERT_QUERY_STR) 
        cursor.close()
        connection.commit()
        connection.close()
        

def _get_data_and_add_to_raw_pd() -> None:
    pg_hook = PostgresHook(postgres_conn_id = 'greenplum')
    
    engine = pg_hook.get_sqlalchemy_engine()
    connection = pg_hook.get_conn()
    """ get data """
    with connection.cursor() as cursor:
        request_str: str = "SELECT * FROM public.mock_data;"
    
        cursor.execute(request_str) 
        results = cursor.fetchall()
        print(f"results: {results}\n")
        
        cursor.execute(SQL_STR_DICT['SELECT_COLUMN_NAMES'])  
        columns = cursor.fetchall()
        print(f"columns: {columns}\n")
        
        columns_lst: list = list()
        for col in columns:
            columns_lst.append(col[0])
        
        dataframe_pd = pd.DataFrame(results, columns = columns_lst)
        dataframe_pd['report_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(dataframe_pd.info())
        
        """ insert data """
        dataframe_pd.to_sql(name = 'mock_data_pandas', 
                            con = engine, 
                            schema = 'raw',
                            if_exists='append',
                            index = False)
        
        cursor.close()
        connection.commit()
        connection.close()



        
def _branch_schema() -> str:
    pg_hook = PostgresHook(postgres_conn_id = 'greenplum')
    connection = pg_hook.get_conn()
    
    with connection.cursor() as cursor:
        
        cursor.execute(SQL_STR_DICT["CHECK_RAW_SCHEMA_STR"])
        data = cursor.fetchall()
        print(f"data: {data}\n")
        flag: bool = False
        
        for index, value in enumerate(data):
            print(f"index: {index}, value: {value}.")
            if value[0] == "raw":
                flag = True
            
        if flag:
            print('raw schema is exists')
            return "sckip_creating_schema"
        else:
            print('raw schema is not exists')
            return "creating_schema"
  
    
def _branch_table() -> str:
    pg_hook = PostgresHook(postgres_conn_id = 'greenplum')
    connection = pg_hook.get_conn()
    
    with connection.cursor() as cursor:
        
        cursor.execute(SQL_STR_DICT["SELECT_TABLES_FROM_RAW"])
        data = cursor.fetchall()
    
        flag: bool = False
        
        for index, value in enumerate(data):
            print(f"index: {index}, value: {value}.")
            if value[0] == "mock_data_pandas":
                flag = True
            
        if flag:
            print('raw schema is exists')
            return "sckip_creating_mock_data_pandas"
        else:
            print('raw schema is not exists')
            return "creating_table_mock_data_pandas"

    
""" DAG """
with DAG(
    'greenplum_postgres_example',
    default_args = default_args,
    schedule_interval = "* 5 * * *",
    catchup = False
    ) as dag:
    
    start_dag = DummyOperator(task_id = 'start_dag', dag = dag)
    end_dag = DummyOperator(task_id = 'end_dag', dag = dag)
    
    Link_1 = DummyOperator(task_id = 'Link_1', dag = dag, trigger_rule='one_success')
    Link_2 = DummyOperator(task_id = 'Link_2', dag = dag, trigger_rule='one_success')
    Link_3 = DummyOperator(task_id = 'Link_3', dag = dag, trigger_rule='none_failed_min_one_success')
    
    """ get schemas part """
    branch_chek_schemas = BranchPythonOperator(task_id = 'branch_chek_schemas',
                                               python_callable = _branch_schema,
                                               dag = dag)
    """ get tables part """
    branch_chek_tables = BranchPythonOperator(task_id = 'branch_chek_tables',
                                              python_callable = _branch_table,
                                              dag = dag)
    
    """ либо инициализируем схему либо пропускаем """
    sckip_creating_schema = DummyOperator(task_id = 'sckip_creating_schema', dag = dag)
    creating_schema = PostgresOperator(task_id = 'creating_schema', 
                                       sql = SQL_STR_DICT["CREATE_SCHEMA_STR"],
                                       postgres_conn_id = 'greenplum',
                                       autocommit = True, 
                                       dag = dag)
    creating_table_mock_data = PostgresOperator(task_id = 'creating_table_mock_data', 
                                                sql = SQL_STR_DICT["CREATE_TABLE_STR"],
                                                postgres_conn_id = 'greenplum',
                                                autocommit = True, 
                                                dag = dag,
                                                trigger_rule='one_success')
    
    """ либо инициализируем таблицу либо пропускаем """
    sckip_creating_mock_data_pandas = DummyOperator(task_id = "sckip_creating_mock_data_pandas", dag = dag)
    creating_table_mock_data_pandas = PostgresOperator(task_id = 'creating_table_mock_data_pandas', 
                                                       sql = SQL_STR_DICT["CREATE_TABLE_STR_PD"],
                                                       postgres_conn_id = 'greenplum',
                                                       autocommit = True, 
                                                       dag = dag,
                                                       trigger_rule='one_success')
    
    
    """ создаем """
    get_data = PythonOperator(task_id = 'get_data',
                              python_callable = _get_data_and_add_to_raw,
                              dag = dag)
    
    get_data_pd = PythonOperator(task_id = 'get_data_pd',
                                 python_callable = _get_data_and_add_to_raw_pd,
                                 dag = dag)
    
    
    
    """ CONSTRUCTING GRAPH """
    start_dag >> branch_chek_schemas >> [sckip_creating_schema, creating_schema] >> Link_2 >> creating_table_mock_data >> Link_1 >> Link_3
    
    Link_2 >> branch_chek_tables >> [sckip_creating_mock_data_pandas, creating_table_mock_data_pandas] >> Link_3
    
    Link_3 >> [get_data, get_data_pd] >> end_dag