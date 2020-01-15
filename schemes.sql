create table scripts
(
    script_id    serial not null Constraint script_id_pk PRIMARY KEY,
    script_title text not null,
    py_script    text,
    xml_script   text,
    is_enabled   boolean default false
);