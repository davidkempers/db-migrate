set long 100000
set head off
set echo off
set pagesize 0
set verify off
set feedback off
spool schema.out
select object_name, dbms_metadata.get_ddl(object_type, object_name)
from
(
    select 'TABLESPACE' as object_type, tablespace_name as object_name from dba_tablespaces
    where tablespace_name not in ('SYSTEM', 'SYSAUX', 'UNDOTBS1', 'TEMP', 'USERS')
);
