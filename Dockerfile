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

# Add command scripts
ADD scripts /scripts
RUN chmod -R +x /scripts

VOLUME ["/changelogs"]

WORKDIR /

ENTRYPOINT ["/scripts/run.sh"]
