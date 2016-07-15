
select dbms_metadata.get_ddl('USER', u.username) AS ddl, u.username as owner, 'USER'  as object_name, 'USER' as object_type
from dba_users u
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('TABLESPACE_QUOTA', tq.username) AS ddl, tq.username as owner,
 'TABLESPACE_QUOTA' as object_name, 'TABLESPACE_QUOTA' as object_type
from   dba_ts_quotas tq
join dba_users u on tq.username = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('ROLE_GRANT', rp.grantee) AS ddl, rp.grantee as owner,
 'ROLE_GRANT' as object_name, 'ROLE_GRANT' as object_type
from   dba_role_privs rp
join dba_users u on rp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('OBJECT_GRANT', tp.grantee) AS ddl, tp.grantee as owner,
 'OBJECT_GRANT' as object_name, 'OBJECT_GRANT' as object_type
from   dba_tab_privs tp
join dba_users u on tp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
union all
select dbms_metadata.get_granted_ddl('DEFAULT_ROLE', rp.grantee) AS ddl, rp.grantee as owner,
 'DEFAULT_ROLE' as object_name, 'DEFAULT_ROLE' as object_type
from dba_role_privs rp
join dba_users u on rp.grantee = u.username
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
and rp.default_role = 'YES'
union all
select dbms_metadata.get_ddl('PROFILE', u.profile) AS ddl, u.username as owner,
 'PROFILE' as object_name, 'PROFILE' as object_type
from dba_users u
where (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
    or u.username in ({users}))
and u.profile <> 'DEFAULT'
