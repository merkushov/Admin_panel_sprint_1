import factory
from faker import Faker
# from movies.models import Movie, Genre
# from movies.tests.factories.genre_factory import GenreFactory
import movies.models
from movies.tests.factories.movie_type_factory import MovieTypeFactory
from movies.tests.factories.person_role_factory import PersonRoleFactory
# import random

fake = Faker(['ru_RU'])
Faker.seed(0)


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'movies.Movie'

    title = factory.Sequence(lambda _: fake.text(max_nb_chars=50))
    description = factory.Sequence(lambda _: fake.text(max_nb_chars=500))
    imdb_identifier = factory.Sequence(
        lambda _: 'tt{}'.format(
            fake.unique.random_int(min=10000000, max=100000000)
        )
    )
    creation_date = factory.Sequence(lambda _: fake.date())
    file_path = factory.Sequence(
        lambda _: fake.file_path(depth=5, category='video')
    )
    rating = factory.Sequence(
        lambda _: fake.pyfloat(right_digits=1, min_value=0, max_value=10)
    )
    type = factory.SubFactory(MovieTypeFactory)


class MovieGenreRandomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'movies.MovieGenre'

    movie_id = factory.LazyAttribute(
        lambda o: fake.pyint(
            min_value=o.min_movie,
            max_value=o.max_movie,
        )
    )
    genre_id = factory.LazyAttribute(
        lambda o: fake.pyint(
            min_value=o.min_genre,
            max_value=o.max_genre,
        )
    )

    class Params:
        min_movie = 1
        max_movie = 1
        min_genre = 1
        max_genre = 1


class MoviePersonRoleRandomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'movies.MoviePersonRole'

    movie_id = factory.LazyAttribute(
        lambda o: fake.pyint(
            min_value=o.min_movie,
            max_value=o.max_movie,
        )
    )

    person_id = factory.LazyAttribute(
        lambda o: fake.pyint(
            min_value=o.min_person,
            max_value=o.max_person,
        )
    )

    # person_role_id = 1
    person_role = factory.SubFactory(PersonRoleFactory)

    class Params:
        min_movie = 1
        max_movie = 1
        min_person = 1
        max_person = 1
