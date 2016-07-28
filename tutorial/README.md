#  DB Migrate Tutorial

Clone this respository for an interactive tutorial

```
git clone https://github.com/davidkempers/db-migrate.git
```

Install db-migrate. This will build the docker image and copy the dbmigrate script to /usr/local/bin

```
cd db-migrate
sudo ./install.sh
```

Create a test branch to play along with

```
git checkout -b myfeaturetest
```

Pull down a docker image of oracle XE. Thanks to Wei-Ming Wu for providing this on github:
https://github.com/wnameless/docker-oracle-xe-11g

```
docker run -d -p 49160:22 -p 49161:1521 -e ORACLE_ALLOW_REMOTE=true wnameless/oracle-xe-11g
```

### Initial installation

Lets start off by creating a simple database schema with a few talbes and a view.

I have already created these in the branch `step1`.

```
git merge step1 --no-commit --no-ff
```

The generator will look for new files added to git (hence why we didn't ato commit on the merge)

Run git status to check your changes

```
git status
```

Now run the generator

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info generate
```

You should see that a install.xml is created in your tutorial root. We can now apply the update.

Run with the `-o` option to show the SQL output first

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info update install -o
```

Now apply the change

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info update install
```

Commit changes and Tag our source control

```
git commit -m "Database Install"
git tag v0.1
```

### Update schema

I have already created a set of changes in the branch `step2`.

```
git merge step2 --no-commit --no-ff
```

Run git status to check your changes

```
git status
```

Now run the generator

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info generate
```

A file update.xml will be greated in /tutorial and master.xml created in /tutorial/v1.0

Now apply the change

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info update install
```

Commit changes and Tag our source control

```
git commit -m "Database Update v1.0"
git tag v1.0
```

### Rollback


We can roll back to any tag including install. In this case we will rollback to `instal`

View the output sql by including the `-o` option

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info rollback -o install
```

Then run the change

```
dbmigrate -s tutorial -d system/oracle@192.168.59.51:49161/xe -l info rollback install
```
