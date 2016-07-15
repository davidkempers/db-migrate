select dbms_metadata.get_ddl(object_type, object_name, owner) as ddl, owner, object_name, object_type
from
(
    select
        owner,
        object_name,
        decode(object_type,
            'DATABASE LINK',     'DB_LINK',
            'JOB',               'PROCOBJ',
            'PACKAGE',           'PACKAGE_SPEC',
            'PACKAGE BODY',      'PACKAGE_BODY',
            'TYPE',              'TYPE_SPEC',
            'TYPE BODY',         'TYPE_BODY',
            'MATERIALIZED VIEW', 'MATERIALIZED_VIEW',
            object_type
        ) object_type
    from dba_objects
    join dba_users u on owner = u.username
    where object_type not in ('LOB', 'INDEX') -- table wil; have these
    and (u.account_status = 'OPEN' and u.username not in ('SYSTEM', 'SYS', 'ANONYMOUS')
        or u.username in ({users}))
)
