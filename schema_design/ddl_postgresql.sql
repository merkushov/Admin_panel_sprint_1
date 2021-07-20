CREATE SCHEMA content;

CREATE EXTENSION "uuid-ossp";
SET search_path TO content,public;

-- Возрастной ценз фильма
CREATE TABLE content.certificates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX certificates_name_uidx ON certificates (name);

-- Тип контента (фильма, сериал и т.п.)
CREATE TABLE content.movie_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX movie_types_name_uidx ON content.movie_types (name);

-- Фильмы
CREATE TABLE content.movies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    creation_date DATE,
    certificate_id INT,
    type_id INT NOT NULL,
    file_path TEXT,
    imdb_identifier VARCHAR(16),
    imdb_rating NUMERIC(3,1) DEFAULT 0 NOT NULL
        CONSTRAINT "between_0_and_10" CHECK (imdb_rating >=0 AND imdb_rating <= 10),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX movies_imdb_identifier_uidx ON content.movies (imdb_identifier);

ALTER TABLE content.movies
    ADD CONSTRAINT fk_movies_certificates
    FOREIGN KEY (certificate_id)
    REFERENCES certificates (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

ALTER TABLE content.movies
    ADD CONSTRAINT fk_movies_movie_types
    FOREIGN KEY (type_id)
    REFERENCES movie_types (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

-- Жанры (экшн, комедия, драмма и т.п.)
CREATE TABLE content.genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX genres_name_uidx ON content.genres (name);

CREATE TABLE content.genre_movie (
    id BIGSERIAL PRIMARY KEY,
    movie_id UUID NOT NULL,
    genre_id int NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX genre_movie_uidx ON content.genre_movie (movie_id, genre_id);

ALTER TABLE content.genre_movie
    ADD CONSTRAINT fk_genre_movie_movies
    FOREIGN KEY (movie_id)
    REFERENCES movies (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

ALTER TABLE content.genre_movie
    ADD CONSTRAINT fk_genre_movie_genres
    FOREIGN KEY (genre_id)
    REFERENCES genres (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

-- Персоны и Роли персон в фильме
CREATE TABLE content.persons (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    full_name VARCHAR(500) NOT NULL,
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX persons_full_name_uidx ON content.persons (full_name);

-- Роли персон (актёр, режисёр, сценарист и т.п.)
CREATE TABLE content.person_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content.movie_person_role (
    id BIGSERIAL PRIMARY KEY,
    movie_id UUID NOT NULL,
    person_id UUID NOT NULL,
    person_role_id INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX movie_person_role_uidx ON content.movie_person_role (movie_id, person_role_id, person_id);

ALTER TABLE content.movie_person_role
    ADD CONSTRAINT fk_movie_person_role_movies
    FOREIGN KEY (movie_id)
    REFERENCES movies (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

ALTER TABLE content.movie_person_role
    ADD CONSTRAINT fk_movie_person_role_persons
    FOREIGN KEY (person_id)
    REFERENCES persons (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;

ALTER TABLE content.movie_person_role
    ADD CONSTRAINT fk_erson_person_role_movie_person_roles
    FOREIGN KEY (person_role_id)
    REFERENCES person_roles (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION;
