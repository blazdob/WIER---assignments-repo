# conda setup

conda packages:
- notebook: for jupyter notebook
- psycopg2: python driver for PostgreSQL

```
conda install notebook psycopg2
```

# Docker

Database user and password are user:password

- open powershell
- activate conda environment: `conda activate wier`
- change directory to pa1 folder of repository

- first time database container run: `docker run --name postgresql-wier -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -v $PWD/db/pgdata:/var/lib/postgresql/data -v $PWD/db/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12`

- to stop database container: `docker stop postgresql-wier`
- to start database container: `docker start postgresql-wier`
- to enter PostgreSQL "shell": `docker exec -it postgresql-wier psql -U user`
- to check logs: `docker logs -f postgresql-wier`