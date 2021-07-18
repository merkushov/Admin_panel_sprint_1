import dataclasses
from dataclasses import dataclass, field

import json
import sqlite3
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_batch
import uuid

@dataclass(frozen=True)
class Person():
    __slots__ = ("id", "name")
    id: str
    name: str

@dataclass(frozen=True)
class Writer(Person): pass

@dataclass(frozen=True)
class Actor(Person): pass

@dataclass(frozen=False)
class Movie:
    # __slots__ = ("id", "title", "imdb_rating", "genres", "description", "directors", "writers", "actors")
    imdb_identifier: str
    title: str
    # uuid: str
    imdb_rating: float = field(default=0.0)
    genres: list = field(default_factory=list)
    description: str = field(default='')
    directors: list = field(default_factory=list)
    writers: list[Writer] = field(default_factory=list)
    actors: list[Actor] = field(default_factory=list)


class PostgresSaver():
    def __init__(self, conn: _connection) -> None:
        self.pg_connection = conn

    def save_persons_data(self, persons: list):
        cur = self.pg_connection.cursor()

        execute_batch(
            cur,
            "INSERT INTO content.persons (full_name) VALUES (%s) ON CONFLICT (full_name) DO NOTHING",
            [(person_name,) for person_name in persons]
        )

        self.pg_connection.commit()
        cur.close()

        return True

    def save_genres_data(self, genres: list):
        cur = self.pg_connection.cursor()

        execute_batch(
            cur,
            "INSERT INTO content.genres (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            [(genre_name,) for genre_name in genres]
        )

        self.pg_connection.commit()
        cur.close()

        return True

    def save_movies_data(self, movies: list[Movie]):
        cur = self.pg_connection.cursor()

        cur.execute("SELECT id FROM content.movie_types WHERE name=%s", ('movie',))
        movie_type = cur.fetchone()

        if not movie_type:
            raise psycopg2.DataError("There is no movie_type with name 'movie'")

        # Создаём Фильмы
        execute_batch(
            cur,
            "INSERT INTO content.movies (title, type_id, imdb_identifier, imdb_rating, description) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (imdb_identifier) DO NOTHING",
            [ ( m.title, movie_type[0], m.imdb_identifier, m.imdb_rating, m.description ) for m in movies ],
        )

        self.pg_connection.commit()

        # Связываем Фильмы и Жанры
        genre_movie = {}
        for movie in movies:
            for genre in movie.genres:
                genre_movie.setdefault(genre, []).append(movie.imdb_identifier)

        execute_batch(
            cur,
            "INSERT INTO content.genre_movie (movie_id, genre_id)"
            "       SELECT m.id, g.id"
            "           FROM movies m LEFT JOIN (SELECT id FROM genres WHERE name=%s) g ON 1=1"
            "           WHERE m.imdb_identifier IN %s"
            "   ON CONFLICT (movie_id, genre_id) DO NOTHING",
            [ ( genre, tuple(genre_movie[genre]) ) for genre in genre_movie.keys() ]
        )

        self.pg_connection.commit()

        # Связываем Фильмы и Персоны (актёров, режисёров, сценаристов)
        movie_person_role = {}
        for movie in movies:
            movie_person_role.setdefault(movie.imdb_identifier, {}).setdefault('actors', ['stumb'])
            movie_person_role.setdefault(movie.imdb_identifier, {}).setdefault('directors', ['stumb'])
            movie_person_role.setdefault(movie.imdb_identifier, {}).setdefault('writers', ['stumb'])
            for actor in movie.actors:
                movie_person_role[movie.imdb_identifier]['actors'].append(actor.name)
            for director in movie.directors:
                movie_person_role[movie.imdb_identifier]['directors'].append(director)
            for writer in movie.writers:
                movie_person_role[movie.imdb_identifier]['writers'].append(writer.name)

        execute_batch(
            cur,
            "INSERT INTO content.person_person_role_movie (movie_id, person_id, person_role_id)"
            "       SELECT m.id, p.id, pr.id"
            "           FROM content.movies m"
            "               INNER JOIN (SELECT id FROM content.persons WHERE full_name IN %s) p ON 1=1"
            "               INNER JOIN (SELECT id FROM content.person_roles WHERE name = 'actor') pr ON 1=1"
            "           WHERE m.imdb_identifier=%s"
            "       UNION ALL"
            "       SELECT m.id, p.id, pr.id"
            "           FROM content.movies m"
            "               INNER JOIN (SELECT id FROM content.persons WHERE full_name IN %s) p ON 1=1"
            "               INNER JOIN (SELECT id FROM content.person_roles WHERE name = 'writer') pr ON 1=1"
            "           WHERE m.imdb_identifier=%s"
            "       UNION ALL"
            "       SELECT m.id, p.id, pr.id"
            "           FROM content.movies m"
            "               INNER JOIN (SELECT id FROM content.persons WHERE full_name IN %s) p ON 1=1"
            "               INNER JOIN (SELECT id FROM content.person_roles WHERE name = 'director') pr ON 1=1"
            "           WHERE m.imdb_identifier=%s"
            "   ON CONFLICT (movie_id, person_id, person_role_id) DO NOTHING",
            [
                (
                    tuple(movie_person_role[imdb_key]['actors']),  imdb_key,
                    tuple(movie_person_role[imdb_key]['writers']),  imdb_key,
                    tuple(movie_person_role[imdb_key]['directors']),  imdb_key,
                ) for imdb_key in movie_person_role ]
        )

        print("Movies inserted...")

        self.pg_connection.commit()
        cur.close()

        return True

class SQLiteLoader():
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.sqlite_connection = conn

    def _get_movies(self, start: int, limit: int):
        sql = f"SELECT * FROM movies LIMIT {start}, {limit}"
        return self.sqlite_connection.execute(sql).fetchall()

    def _get_movie_writers(self, writer: str, writers: str) -> list:
        unique_data = {}
        if writer:
            unique_data.setdefault(writer, None)

        if writers:
            writers = json.loads(writers)
            for w in writers:
                unique_data.setdefault(w["id"], None)

        in_placeholders = ','.join(['?'] * len(unique_data))

        rows = self.sqlite_connection.execute(
            f"SELECT id, name FROM writers WHERE id IN ({in_placeholders}) AND name != 'N/A'",
            list(unique_data.keys())
        ).fetchall()

        result = []
        for row in rows:
            result.append(Writer(row["id"], row["name"]))

        return result

    def _get_movie_actors(self, movie_id: str):
        rows = self.sqlite_connection.execute(
            ''.join(
                (
                    "SELECT a.id, a.name ",
                    "FROM actors a LEFT JOIN movie_actors ms ON a.id=ms.actor_id ",
                    "WHERE ms.movie_id = ? AND a.name != 'N/A'",
                )
            ),
            (movie_id,)
        ).fetchall()

        result = []
        for row in rows:
            result.append(Actor(row["id"], row["name"]))

        return result

    def _check_na(self, string: str) -> bool:
        if string and string == 'N/A':
            return True

        return False

    def load_movies(self, start: int, limit: int) -> list:
        sqlite_movies = self._get_movies(start, limit)
        
        movies = []
        for row in sqlite_movies:
            movies.append(
                Movie(
                    # uuid = str(uuid.uuid4()),
                    imdb_identifier = row["id"],
                    imdb_rating = 0.0 if self._check_na(row["imdb_rating"]) else float(row["imdb_rating"]),
                    genres = row["genre"].replace(' ', '').split(','),
                    title = row["title"],
                    description = '' if self._check_na(row["plot"]) else row["plot"],
                    directors = [] if self._check_na(row["director"]) else [x.strip() for x in row['director'].split(',')],
                    writers = self._get_movie_writers(row["writer"], row["writers"]),
                    actors = self._get_movie_actors(row["id"])
                )
            )

        return movies

    def load_persons(self, start: int, limit: int) -> list:
        persons = []

        rows = self.sqlite_connection.execute(f"SELECT name FROM actors LIMIT {start}, {limit}").fetchall()
        for row in rows:
            persons.append(row["name"])

        rows = self.sqlite_connection.execute(f"SELECT director FROM movies LIMIT {start}, {limit}").fetchall()
        for row in rows:
            if not self._check_na(row["director"]):
                for x in row['director'].split(','):
                    persons.append(x.strip())

        rows = self.sqlite_connection.execute(f"SELECT name FROM writers LIMIT {start}, {limit}").fetchall()
        for row in rows:
            persons.append(row["name"])

        return persons

    def load_genres(self, start: int, limit: int) -> list:
        genres = {}

        rows = self.sqlite_connection.execute(f"SELECT genre FROM movies LIMIT {start}, {limit}").fetchall()
        for row in rows:
            for genre in row["genre"].replace(' ', '').split(','):
                genres.setdefault(genre, None)

        return list(genres.keys())

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    limit = 500

    # Загрузка справочника Персон (SQLite: Актёры, Сценаристы и Режисёры)
    start = 0
    while 1:
        data = sqlite_loader.load_persons(start, limit)
        if len(data) == 0:
            break

        postgres_saver.save_persons_data(data)
        start += limit

    # Загрузка справочника Жанров
    start = 0
    while 1:
        data = sqlite_loader.load_genres(start, limit)
        if len(data) == 0:
            break

        postgres_saver.save_genres_data(data)
        start += limit

    # Загрузка каталога Фильмов и всех связей с Жанрами и Персонами
    start = 0
    while 1:
        data = sqlite_loader.load_movies(start, limit)
        if len(data) == 0:
            break

        # print(json.dumps(data, cls=EnhancedJSONEncoder))
        postgres_saver.save_movies_data(data)
        start += limit


if __name__ == '__main__':
    pg_dsl = {
        'dbname': 'movie_catalog',
        'user': 'postgres',
        # 'password': 1234,
        'password': 'qdQd03NdkJDIb3293jkhasdejd',
        'host': '127.0.0.1',
        'port': 5432,
        'options': '-c search_path=content',
    }

    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**pg_dsl, cursor_factory=DictCursor) as pg_conn:
        sqlite_conn.row_factory = sqlite3.Row
        load_from_sqlite(sqlite_conn, pg_conn)
