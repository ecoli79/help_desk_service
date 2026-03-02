--
-- PostgreSQL schema for bot_support
--

CREATE TABLE IF NOT EXISTS employee (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    firstname   varchar NOT NULL,
    lastname    varchar NOT NULL,
    username    varchar NOT NULL UNIQUE,
    password    varchar NOT NULL,
    email       varchar NOT NULL,
    "position"  varchar NOT NULL,
    date_insert date    NOT NULL,
    date_update date    NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_username   varchar,
    telegram_fullname   varchar,
    date_insert         timestamp NOT NULL,
    date_update         timestamp
);

CREATE TABLE IF NOT EXISTS ticket_types (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type_name   varchar NOT NULL,
    date_insert timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_update timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ticket_types (type_name) VALUES
    ('Подписание'),
    ('Оборудование'),
    ('Доступ к системам'),
    ('Другое');

CREATE TABLE IF NOT EXISTS tickets (
    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id_created     bigint  NOT NULL REFERENCES users (id),
    ticket_type_id      integer NOT NULL REFERENCES ticket_types (id),
    ticket_text         varchar NOT NULL,
    telegram_chatid     varchar NOT NULL,
    telegram_message_id bigint,
    max_message_id      varchar,
    is_done             boolean NOT NULL DEFAULT false,
    sended              boolean NOT NULL DEFAULT false,
    is_working          boolean DEFAULT false,
    text_response       varchar,
    note                varchar,
    employee_id         integer REFERENCES employee (id),
    date_insert         timestamp NOT NULL,
    date_update         timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    image_path  varchar   NOT NULL,
    ticket_id   bigint    NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    date_insert timestamp NOT NULL,
    date_update timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS voices (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    voice_path  varchar   NOT NULL,
    ticket_id   bigint    NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    date_insert timestamp NOT NULL,
    date_update timestamp NOT NULL
);
