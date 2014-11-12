The migrations in the alembic/versions contain the migrations.

Before running this migration ensure that the database cue exists.

Currently the database connection string is in cue/db/migration/alembic.ini
but this should eventually be pulled out into an cue configuration file.
Set connection string is set by the line:
sqlalchemy.url = mysql://<user>:<password>@localhost/<database>

To run migrations you must first be in the cue/db/migrate directory.

To migrate to the most current version run:
$ alembic upgrade head

To downgrade one migration run:
$ alembic downgrade -1