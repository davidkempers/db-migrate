create or replace view cmpny.employeedepartments_view 
    as select e.first_name, e.last_name
    from cmpny.employees e
    join cmpny.departments d on d.id = e.department_id