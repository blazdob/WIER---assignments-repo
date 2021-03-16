# conda setup

## create conda environment
`conda create -n wier`

## package installation
- notebook: for jupyter notebook
- psycopg2: python driver for PostgreSQL
`conda install notebook psycopg2`

# pip packages

Some python packages needed by crawler can be installed with pip:
`pip install -r requirements.txt`

# PostgreSQL in Docker setup (with db/init-scripts mount)

- change directory to pa1 folder of repository

- first time database container run:
  `docker run --name postgresql-wier -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -v $PWD/db/pgdata:/var/lib/postgresql/data -v $PWD/db/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12`

# PostgreSQL and pgAdmin in Docker setup (no db/init-scripts mount)

- change directory to `pa1` folder of repository

- run database container:
  `docker run --name postgresql-wier -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -v $PWD/db/pgdata:/var/lib/postgresql/data -p 5432:5432 -d postgres:12`

- run pgAdmin container (you can use anything that looks like email address, it doesn't have to be valid):
  `docker run --name pgadmin-wier -p 80:80 -e 'PGADMIN_DEFAULT_EMAIL=email@domain.com' -e 'PGADMIN_DEFAULT_PASSWORD=password' -d dpage/pgadmin4`

- navigate your browser to `http://localhost` and log in with provided email and password

- navigate to **Add New Server** on Welcome page

- fill in **Name** entry (e. g. postgresql-wier) in **General** tab

- **For Docker on WSL2, didn't check on other Docker setup options for Windows!!!**: open command prompt and type: `ipconfig`
   look for IP address of WSL adapter in the output of ipconfig command

- fill in **Host name/address** entry in **Connection** tab with IP (WSL2) or localhost (otherwise?)

- fill in **Username** and **Password** used for database container and save

- select **Servers -> postgresql-wier (or your server name) -> Databases -> postgres**

- with database selected open now available **Tools -> Query Tool** from main toolbar

- paste contents of `db/init-scripts/crawldb.sql` into **Query Editor**

- execute query (toolbar or F5)

- you can now logout and close the browser

# Operating containers

- start containers:
  `docker start container-name` (e. g. postgresql-wier)

- stop containers:
  `docker stop container-name`

- to enter PostgreSQL "shell":
  `docker exec -it postgresql-wier psql -U user`

- to check logs:
  `docker logs -f container-name`

# Config file

`examples/config.ini` provides example config file for crawler. This file can
be copied to the `pa1` folder and modified as necessary.