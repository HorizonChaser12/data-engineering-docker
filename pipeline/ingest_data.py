#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import logging
import logging
import sys
from tqdm.auto import tqdm

# Configure logging to output to standard output in the notebook
logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    level=logging.INFO, # Set the desired minimum log level (e.g., logging.DEBUG, logging.WARNING)
    stream=sys.stdout
)

# Get a logger instance
logger = logging.getLogger('notebook')

# Read a sample of the data
# This file is already present in Github and thus we are just fetching that url to get the data, for simplicity and configurable, we are breaking the url into parts i.e prefix and then the file name.
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
# creating a dataframe by reading the csv file and the no. of rows we want to read using Pandas
df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)


# In[2]:


# this shows the top 5 data of the dataframe we created above
df.head()


# In[3]:


# This shows the no. of rows and no. of columns of the datafram
df.shape


# In[4]:


# This shows all the data types of the columns present in the dataframe, mostly 18 as we saw earlier.
df.dtypes


# In[5]:


# We are using sqlalchemy to push the dataframe through SQL to the Postgres System running in our docker
from sqlalchemy import create_engine

# used to create the SQLAlchemy engine and connect it to Postgres
engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')


# In[6]:


# This prints the schema of the dataframe through SQL using the SQLAlchemy engine
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))


# In[24]:


# Sometimes we get issue while reading the csv so we are differentiating all the needed parts like column_name:data_types, parse_dates etc etc.
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

# Now the older dataframe is now overwritten with the new one where we are aligning it with the datatypes we have mentioned and what will be the dates column etc etc.

df = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)

# Prints the table without any rows but all the columns
# .to_sql performs a DB operation and the output "0" shows that it has inserted 0 rows.
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')


# In[26]:


# We are now using a iterator to insert the data inside the table in parts of chunks mainly defined in the below code.
df_iter = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)

# To check the length of each chunk and how many parts are there.
# So I tried the below code and everytime the last chunk only gets inserted, its due to how iterator works, as it is consumed over here the next for loop int the next cell only inserts the last chunk which is not even done in the foor loop, its done in the first line of code I have written.
# for df_chunk in tqdm(df_iter):
#     print(len(df_chunk))




# In[27]:


# # Used to insert the chunk into the postgres table
# df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

# insert the DataFrame with 0 rows but ALL columns with datatypes, create table schema (no data)
df_chunk.head(0).to_sql(
    name="yellow_taxi_data",
    con=engine,
    if_exists="replace"
    )
print("Table created")

for df_chunk in tqdm(df_iter):
    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )
    print("Inserted:", len(df_chunk))


# In[ ]:




