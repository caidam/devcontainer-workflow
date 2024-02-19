# datastats_service.py
import pandas as pd
from db_utils import create_db_engine

def execute_query(sql_query, *params):
    engine = create_db_engine()
    with engine.connect() as connection:
        df = pd.read_sql_query(sql_query, connection, params=params)
        json_data = df.to_json(orient='records')
    return json_data

def get_top_5_data():
    sql_query = "select * from datastats limit 5"
    return execute_query(sql_query)

def get_offer_evolution_data():
    sql_query = """
    select date_trunc('day', date_of_search::date)::date::text as ref_day, count(*) as nb_offer
    from datastats d 
    group by 1
    order by 1;
    """
    return execute_query(sql_query)

def get_top_skills_data(job_search=None):
    # Use COALESCE to handle NULL values and provide a default value ('%') if job_search is not provided
    sql_query = """
    select technologie, count(*) as nb_offer
    from datastats
    where job_search = coalesce(%s, job_search)
    group by 1
    order by 2 desc
    limit 10;
    """
    return execute_query(sql_query, job_search)

def get_top_5_jobs():
    sql_query="""
    select job_search, count(*) as nb_jobs
    from datastats d 
    group by 1
    order by 2 desc
    limit 5;
    """
    return execute_query(sql_query)