 select dbms_metadata.get_ddl('REF_CONSTRAINT',c.constraint_name,c.owner) as ddl, c.owner, c.constraint_name, 'constraint' as object_type from dual d
   ,all_constraints c
   where constraint_type not in ('P', 'C', 'U', 'O', 'F')
   and c.owner not in ('SYS', 'SYSTEM', 'WMSYS', 'SYSMAN','MDSYS','ORDSYS','XDB', 'WKSYS','OLAPSYS', 'DBSNMP', 'DMSYS','CTXSYS','WK_TEST', 'ORDPLUGINS', 'OUTLN', 'EXFSYS')
   