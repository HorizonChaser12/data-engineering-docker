#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine, text

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

# Used to run the whole code with command line argument parsing
@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2021, type=int, help='Year of the data')
@click.option('--month', default=1, type=int, help='Month of the data')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')
@click.option('--schema', default='pipeline', help='PostgreSQL schema name')



def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize, schema):
    """Ingest NYC taxi data into Postgres"""
    
    # To connect the postgres database using SQLAlchemy
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')
    
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'



    # We are now using a iterator to insert the data inside the table in parts of chunks mainly defined in the below code.
    df_iter = pd.read_csv(
        url,
        dtype=dtype, # pyright: ignore[reportArgumentType]
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize
    ) # type: ignore


    # A flag to insert the data only once during the first iteration.
    first = True

    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()
    
    for df_chunk in tqdm(df_iter):
    # insert the DataFrame with 0 rows but ALL columns with datatypes, create table schema (no data)
        if first:
            df_chunk.head(0).to_sql(
            name=target_table,
            con=engine,
            if_exists="replace",
            schema=schema
            )
            first = False
            print("Table created")
        # Insert chunk
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            schema=schema
        )
        print("Inserted:", len(df_chunk))


if __name__ == '__main__':
    run()




