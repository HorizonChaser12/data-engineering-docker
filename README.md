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
