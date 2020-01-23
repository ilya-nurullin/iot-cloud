create table scripts
(
    script_id    serial not null Constraint script_id_pk PRIMARY KEY,
    script_title text not null,
    py_script    text,
    xml_script   text,
    is_enabled   boolean default false
);
CREATE TABLE devices
(
    device_id integer GENERATED ALWAYS AS IDENTITY, 
	device_title text,
    is_connected boolean,
    PRIMARY KEY (device_id)
);
