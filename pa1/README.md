# conda setup

## create conda environment
`conda create -n wier python=3.8`

## environment activation
`conda acitvate wier`

## package installation
- notebook: for jupyter notebook
- psycopg2: python driver for PostgreSQL
`conda install notebook psycopg2`

# pip packages
Some python packages needed by crawler can be installed with pip (make sure that conda environment is activated):
`pip install -r requirements.txt`

# PostgreSQL in Docker setup (with db/init-scripts mount)
- change directory to `pa1/crawler` folder of repository
- first time database container run:
  `docker run --name postgresql-wier -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -v $PWD/db/pgdata:/var/lib/postgresql/data -v $PWD/db/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12`

# PostgreSQL and pgAdmin in Docker setup (no db/init-scripts mount)
- change directory to `pa1/crawler` folder of repository
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

# SQL Commands for some crawler operations

- Set all pages that had error to be recrawled in future
  `UPDATE crawldb.page SET page_type_code = 'FRONTIER' WHERE page_type_code = 'ERROR'`
- Get distinct IDs of domains of pages in FRONTIER; useful when seeing how many domains are
  being rotated when using rotation strategy:
  `SELECT DISTINCT ON (site_id) id, site_id, url FROM crawldb.page WHERE page_type_code = 'FRONTIER'`
- Get number of processed pages:
  `SELECT COUNT(*) FROM crawldb.page WHERE page_type_code != 'FRONTIER'`

# Operating crawler
- You have to be in `pa1/crawler` directory.
- Run crawler with `python main.py`
- Crawler can be run with arguments: `python main.py -d DEBUG --strategy BATCH_BFS --workers 6`. For more information: `python main.py --help`
- `examples/config.ini.example` provides example config file for crawler. This file can
  be copied to the same folder as `main.py` with name `config.ini` and modified as necessary.
- You can stop the crawler with CTRL-C, preferably during sleep after thread batch is finished. If you try stopping
  it during thread execution, the program won't terminate immediately. The signal will be processed only after
  the threads are finished.
- When you try to stop the program the selenium webdrivers are going to try to reconnect several times before
  finally quitting so you have to be patient for a little while. If you try to end it quickly with CTRL-C again,
  the program will stop faster but with an ugly exception trace. We are not sure whether this is due to a
  certain bug or just selenium not working best with CTRL-C signaling. Sometimes exception might happen while
  initializing selenium webdrivers. We are not sure why that is. In this case just re-run the program.