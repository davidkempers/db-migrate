# Orginal version from https://github.com/sequenceiq/docker-liquibase

FROM java

MAINTAINER David Kempers <http://github/davidkempers/db-migrate>

# download liquibase
# ADD https://github.com/liquibase/liquibase/releases/download/liquibase-parent-3.5.1/liquibase-3.5.1-bin.tar.gz /tmp/liquibase.tar.gz
COPY lib/liquibase-3.5.1-bin.tar.gz /tmp/liquibase.tar.gz

# Create a directory for liquibase
RUN mkdir /opt/liquibase

# Unpack the distribution
RUN tar -xzf /tmp/liquibase.tar.gz -C /opt/liquibase
RUN chmod +x /opt/liquibase/liquibase

# Symlink to liquibase to be on the path
RUN ln -s /opt/liquibase/liquibase /usr/local/bin/

# Get the oracle JDBC driver from http://jdbc.postgresql.org/download.html
# ADD http://www.oracle.com/technetwork/apps-tech/jdbc-112010-090769.html /opt/jdbc_drivers/
COPY lib/ojdbc6.jar /opt/jdbc_drivers/

RUN ln -s /opt/jdbc_drivers/ojdbc6.jar /usr/local/bin/

# install SQL plus
COPY lib/oracle-instantclient12.1-basic-12.1.0.2.0-1.x86_64.rpm /tmp/basic.rpm
COPY lib/oracle-instantclient12.1-sqlplus-12.1.0.2.0-1.x86_64.rpm /tmp/sqlplus.rpm

ENV ORACLE_HOME=/usr/lib/oracle/12.1/client64
ENV PATH=$ORACLE_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$ORACLE_HOME/lib

# COPY config/tnsnames.ora $ORACLE_HOME/network/admin/tnsnames.ora

# install alien to install the RPM. libaio1 is a dependency of sqlplus
RUN apt-get update && apt-get install -y alien libaio1

RUN alien -i /tmp/basic.rpm
RUN alien -i /tmp/sqlplus.rpm

# clean up
RUN rm /tmp/liquibase.tar.gz /tmp/basic.rpm /tmp/sqlplus.rpm

# Add command scripts
ADD scripts /scripts
RUN chmod -R +x /scripts

RUN apt-get install -y python-pip
#python-dev build-essential
#RUN pip install --upgrade pip
RUN pip install gitpython

VOLUME ["/changelogs"]

WORKDIR /changelogs

ENTRYPOINT ["/scripts/run.py"]
