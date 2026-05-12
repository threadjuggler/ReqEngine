# ReqEngine

This is a python fastapi application to create, store, modifiy and administer requirements for safety related applications

proudly developed with the help of claude ai.

Installation:

- git clone this repository 
git clone https://github.com/threadjuggler/ReqEngine.git

- edit the passwords in .env.example to change it from the defaults with a text editor

- copy the eedited .env.example to .env
- cp .env.example .env

- create docker container and start:
docker compose up --build

start your browser and surft to 127.0.0.1:9000


## Database migrations (Alembic)

The schema is managed by Alembic. Migrations live in `alembic/versions/`.
On every container start, the api entrypoint runs `alembic upgrade head` before
launching uvicorn, so a fresh `docker compose up` brings the database to the
latest schema automatically.

Common workflow (run inside the api container):

- show current revision:
  `docker compose exec api alembic current`
- show history:
  `docker compose exec api alembic history`
- create a new revision after editing `models.py`:
  `docker compose exec api alembic revision --autogenerate -m "describe change"`
  then review/edit the generated file in `alembic/versions/` before committing.
- apply pending migrations manually:
  `docker compose exec api alembic upgrade head`
- roll back one step:
  `docker compose exec api alembic downgrade -1`
- mark a pre-existing DB as already migrated without running anything:
  `docker compose exec api alembic stamp head`

