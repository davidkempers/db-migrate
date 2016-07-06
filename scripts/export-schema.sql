set long 300000
set longchunksize 300000
set head off
set echo off
set pagesize 0
set verify off
set feedback off

set colsep ","     -- separate columns with a comma
set pagesize 0   -- No header rows
set trimspool on -- remove trailing blanks
set headsep off  -- this may or may not be useful...depends on your headings.
 set linesize 1000   -- X should be the sum of the column widths
-- set numw X       -- X should be the length you want for numbers (avoid scientific notation on IDs)

-- spool schema.csv
select owner, object_name, object_type, dbms_metadata.get_ddl(object_type, object_name, owner)
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
    where --object_type in ('TABLE')
    owner not in ('SYS', 'OUTLN', 'SYSTEM', 'CTXSYS', 'XDB', 'MDSYS', 'HR', 'FLOWS_FILES', 'APEX_040000')
    and owner = 'NOTIFY'
);
