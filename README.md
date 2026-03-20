# Notes

## How to run PostgreSQL in a Container

```

  docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
  
```  

### Explanation of Parameters

- ```-e``` sets environment variables (user, password, database name)
- ```-v``` ny_taxi_postgres_data:/var/lib/postgresql creates a named volume
  - Docker manages this volume automatically
  - Data persists even after container is removed
  - Volume is stored in Docker's internal storage
- ```-p 5432:5432``` maps port 5432 from container to host
- ```postgres:18``` uses PostgreSQL version 18 (latest as of Dec 2025)

<hr>

&nbsp;

## Connecting to PostgreSQL

Install pgcli through uv module:

`uv add --dev pgcli`

The --dev flag marks this as an devlopement dependency. It will be added to the ```[dependency-groups]``` section of pyproject.toml instead of main dependencies section.
Mostly this is being used to regulate the use of ```uv``` and make the transition while cloning the whole repo smoother.

Now use it to connect to Postgres:

`uv run pgcli -h localhost -p 5432 -u root -d ny_taxi`

- ```uv run``` executes a command in the context of the virtual environment as ```uv``` is present in our .venv.
- ```-h``` is the host. Since we are running it locally we can use ```localhost```.
- ```-p``` is the port.
- ```-u``` is the username which would be root for the deafult access.
- ```-d``` is the database name.
- The password for the root access is not provided and will only be asked after logging in through the command line. And the password would be the same ```root```.

<hr>

&nbsp;

## 1. Ingestion of Data into Postgres

**High level Steps :**

1. Download the CSV file
2. Read it in chunks using Pandas
3. Convert datetime columns
4. Insert data into PostgreSQL using SQLAlchemy

- Please refer to the jupyter notebook [Ingestion.ipynb](Ingestion.ipynb) to see the code for ingestion and proper explanation.

Note:

- We converted the ipynb file to a python script using the code:
`uv run jupyter nbconvert --to=script Ingestion.ipynb`
- Then we are chaning the name of the file using the code:
`mv Ingestion.ipy ingest_data.py`

<hr>

&nbsp;

## Running Postgres through pgAdmin - Database Management Tool

`pgcli` is a handy tool to check your database through the terminal but in the next phases you should have a working webpage based database management tool to make it more convenient and easy to access databases.

### Run pgAdmin Container

<hr>

```

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  dpage/pgadmin4

```

Note:

The `-v pgadmin_data:/var/lib/pgadmin` volume mapping saves pgAdmin settings (server connections, preferences) so you don't have to reconfigure it every time you restart the container.

- It needs 2 environment variable one will be the pdadmin mail and another one will be the password.
- As pgAdmin is a web bases tool, the deafult port is `80`, we are re-routing to `8085` port in our localhost to avoid conflicts.
- Image name is `dpage/pgadmin4`


## Docker Networks

Creating a virtual docker network:

```

docker network create pg-network

```

### Run container on the Same Network

```
# Run postgres on the virtual network we created earlier

docker run -it \
  -e POSTGRES_USER = "root" \
  -e POSTGRES_PASSOWRD = "root" \
  -e POSTGRES_DB = "ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18


# In another terminal run pgAdmin on the same virtual network

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL = "admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD = "root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage\pgadmin4

```

