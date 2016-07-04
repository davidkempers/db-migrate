#  DB Migrate

This is a library for creating and applying liquibase changelogs to an Oracle database. It creates the changelogs by reading the directory structure of the SQL source.

See the tutorial for more information

## Requirements

- Docker
- Git - Your SQL statements under source control (see Export if not)
- Your Oracle DB

## SQL Directory Structure

    +-- sql             <-- Working directory (can have any name)
        +-- .git        <-- git source control (can be in parent directory)
        +-- install     <-- Installation changelogs (create table, sequences, etc)
        +-- latest      <-- Changelogs for replaceable objects (packages, triggers, views, etc)
        +-- v1.0        <-- Changelogs to upgrade to version 1.0
        +-- v2.0        <-- Changelogs to upgrade to version 2.0


To take advantage of the changelog generation, you will need to have your SQL files under Git source control. The generate script will look in the sql working directory first, then work it's way up until the .git repo is found.

You will need to tag Git with your release versions. The tag name **must** match the directory version name.

`install` contains changesets that **must** only be run once when the database is installed. It may contain the following

    +-- install
        +-- indexes
        +-- sequences
        +-- tables
            +-- schemaname
                +-- tablename.sql
        +-- users
            +-- username.sql

`latest` contains replaceable objects. They can be from the initial installation or changes in releases.

    +-- latest
        +-- packages
            +-- schemaname
                +-- packagename.sql
        +-- procedures
        +-- triggers
        +-- types
        +-- views

The other directories contain alteration SQL changes for a release. These **must** only be for changes to objects in the `install` directory or data changes.

    +-- v004
        +-- ticketid                    <-- The ticket the change releates to (eg Jira bugfix)
            +-- schemaname              <-- The schema name for the change
                +-- change.sql          <-- The change in Liquibase SQL format
            +-- schemaname.change.sql   <-- Or just prefix the change with the schema name

## Installation

To nstall dbmigrate run:

```
sudo ./install.sh
```

This script will build the docker image and copy the dbmigrate script to /usr/local/bin

```
docker build -t dbmigrate .
cp ./bin/dbmigrate /usr/local/bin/dbmigrate
```

#### Uninstall

Remove the docker container and dbmigrate script

```
sudo ./uninstall.sh
```

## Running database migrations

Run `dbmigrate --help` to specify the working directory and other options

#### Generate changelog

```
dbmigrate generate [options]
```

#### Update

Update to a version (can include 'install')

```
dbmigrate update [options] <version>
```

#### Rollback

Follow the Liquibase SQL format for includng rollbacks. It is not necesary to include rolback SQL for objects in `latest` if you're versions are tagged in git.

```
dbmigrate rollback [options] <version>
```

#### Export

Export the database schema to SQL. This will create a baseline if you have an existing database that has not been under version control.

```
dbmigrate export [options]
```

#### Diff

Create a schema diff between an update then a rollback. This can be used to check your rollback.

Note: This will not check data changes

```
dbmigrate diff [options] <version>
```

## Git workflow

To automatically generate the changeset copy the pre-commit hook into your .git/hooks

```
cp hooks/pre-commit /path/to/.git/hooks/pre-commit
```

To allow rollback and update database changes when you switch git branches

```
cp hooks/post-checkout /path/to/.git/hooks/post-checkout
```

## Licence

MIT
