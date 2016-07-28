create table cmpny.employees
(
    id number not null enable,
    department_id number not null enable,
    first_name varchar2(50) not null enable,
    last_name varchar2(50) not null enable,
    constraint user_pk primary key (id),
    constraint department_fk
    FOREIGN KEY (department_id)
    REFERENCES cmpny.departments(id)
)
tablespace cmpnydata