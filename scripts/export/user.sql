select dbms_metadata.get_ddl('USER', u.username) AS ddl, 'SYSTEM' as owner, u.username as object_name, 'USER' as object_type
from dba_users u
where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
    or u.username in ({users}))
union all
--select dbms_metadata.get_granted_ddl('TABLESPACE_QUOTA', tq.username) AS ddl, tq.username as owner,
-- 'TABLESPACE_QUOTA' as object_name, 'TABLESPACE_QUOTA' as object_type
--from   dba_ts_quotas tq
--join dba_users u on tq.username = u.username
--where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
--    or u.username in ({users}))
--union all
select dbms_metadata.get_granted_ddl('ROLE_GRANT', rp.grantee) AS ddl, 'SYSTEM' as owner,
 rp.grantee as object_name, 'ROLE_GRANT' as object_type
from   dba_role_privs rp
join dba_users u on rp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('OBJECT_GRANT', tp.grantee) AS ddl, 'SYSTEM' as owner,
 tp.grantee as object_name, 'OBJECT_GRANT' as object_type
from   dba_tab_privs tp
join dba_users u on tp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('DEFAULT_ROLE', rp.grantee) AS ddl, 'SYSTEM' as owner,
 rp.grantee as object_name, 'DEFAULT_ROLE' as object_type
from dba_role_privs rp
join dba_users u on rp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
    or u.username in ({users}))
and rp.default_role = 'YES'
union all
select dbms_metadata.get_ddl('PROFILE', u.profile) AS ddl, 'SYSTEM' as owner, u.username as object_name,
'PROFILE' as object_type
from dba_users u
where (u.account_status = 'OPEN' and u.username not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
    or u.username in ({users}))
and u.profile <> 'DEFAULT'
union all
select distinct dbms_metadata.get_ddl('ROLE', r.role) AS ddl, 'SYSTEM' as owner, r.role as object_name, 'ROLE' as object_type
from   dba_roles r
--join dba_role_privs drp on drp.GRANTED_ROLE = r.role
--where drp.granteeor in ({users})
union all
select to_clob('alter user ' || username || ' quota ' || case max_bytes when -1 then ' unlimited ' else to_char(max_bytes) end || ' on ' || tablespace_name) as ddl,
'SYSTEM' as owner, username as object_name, 'TABLESPACE_QUOTA' as object_type
from dba_ts_quotas
