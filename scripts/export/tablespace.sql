select dbms_metadata.get_ddl(object_type, object_name) as ddl, owner, object_name, object_type
from
(
    select '' as owner, 'TABLESPACE' as object_type, tablespace_name as object_name
    from dba_tablespaces
    where tablespace_name not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
)
