
create user cmpny identified by cmpny;

grant connect to cmpny;

alter user cmpny default tablespace cmpnydata;

alter user cmpny quota unlimited on cmpnydata;