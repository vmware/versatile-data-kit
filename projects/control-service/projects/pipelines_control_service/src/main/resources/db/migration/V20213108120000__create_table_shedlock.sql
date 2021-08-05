create table if not exists shedlock (
    name varchar primary key,
    lock_until timestamp not null,
    locked_at timestamp not null,
    locked_by varchar not null
)
