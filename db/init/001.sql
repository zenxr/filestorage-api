create table filestorage_user (
    id serial primary key not null,
    username varchar(255) not null,
    password varchar(255) not null,
    email varchar(255) not null,
    created_on timestamp not null default now()
);

create table bucket (
    id serial primary key not null,
    name varchar(255) not null,
    created_by int references filestorage_user(id),
    created_on timestamp not null default now(),
    constraint unique_name unique (name)
);

create table file (
    id serial primary key not null,
    path varchar(255) not null,
    bucket_id int references bucket(id),
    created_by int references filestorage_user(id),
    created_on timestamp not null default now(),
    updated_on timestamp,
    constraint unique_file_path_in_bucket unique (path, bucket_id)
);
