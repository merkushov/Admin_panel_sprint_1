from dataclasses import dataclass, field
from django.core.management.base import BaseCommand, CommandError
from movies.tests.factories.certificate_factory import CertificateFactory
from movies.tests.factories.genre_factory import GenreFactory
from movies.tests.factories.person_factory import PersonFactory
from movies.tests.factories.person_role_factory import PersonRoleFactory
from movies.tests.factories.movie_type_factory import MovieTypeFactory
from movies.tests.factories.movies_factory import (
    MovieFactory,
    MovieGenreRandomFactory,
    MoviePersonRoleRandomFactory
)
from movies.models import (
    Certificate,
    Genre,
    MoviePersonRole,
    Person,
    Movie,
    MovieGenre,
)
from django.db.utils import IntegrityError


@dataclass(frozen=False)
class Interval():
    type: str
    min: int = field(default=1)
    max: int = field(default=1)

    def __str__(self) -> str:
        return "min: %s max: %s (%s)" % (self.min, self.max, self.type)

    def normalize(self):
        if self.min == self.max:
            self.min = 1


@dataclass(frozen=False)
class GenreInterval(Interval):
    type: str = field(default='genre')


@dataclass(frozen=False)
class MovieInterval(Interval):
    type: str = field(default='movie')


@dataclass(frozen=False)
class PersonInterval(Interval):
    type: str = field(default='person')


class Command(BaseCommand):
    help = 'Generates a large amount of fake data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count_genres',
            type=int,
            default=1000,
            help='The number of elements (Genre) to generate',
        )
        parser.add_argument(
            '--count_persons',
            type=int,
            default=100000,
            help='The number of elements (Person) to generate'
        )
        parser.add_argument(
            '--count_movies',
            type=int,
            default=50000,
            help='The number of elements (Movies) to generate',
        )
        parser.add_argument(
            '--movie_genre_coeff',
            type=int,
            default=3,
            help='Determines how much more the total '
            'number of links of films with genres will be',
        )
        parser.add_argument(
            '--movie_actor_coeff',
            type=int,
            default=20,
            help='Determines how much more the total '
            'number of links of films with actors will be',
        )
        parser.add_argument(
            '--movie_director_coeff',
            type=int,
            default=2,
            help='Determines how much more the total '
            'number of links of films with directors will be',
        )
        parser.add_argument(
            '--movie_writer_coeff',
            type=int,
            default=3,
            help='Determines how much more the total '
            'number of links of films with writers will be',
        )

    def get_max_pk_id(self, manager):
        result = 1
        if manager.objects.count():
            item = manager.objects.all().order_by("-id")[0]
            result = item.id

        return result

    def fillin_catalog(
            self, factory_manager, manager,
            total_count=10, **kwargs):
        print("Start processing %s (bulk_create)" % manager.__name__)

        factory_options = {}
        if kwargs.get('factory_intervals', None):
            for i in kwargs['factory_intervals']:
                factory_options.setdefault("min_{}".format(i.type), i.min)
                factory_options.setdefault("max_{}".format(i.type), i.max)

        if kwargs.get('factory_params', None):
            for k in kwargs["factory_params"].keys():
                factory_options[k] = kwargs["factory_params"][k]

        print(factory_options)

        if kwargs.get('interval', None):
            kwargs['interval'].min = self.get_max_pk_id(manager)
            factory_manager.reset_sequence(kwargs['interval'].min+1)

        batch_size = 10000
        batches = []
        if total_count > batch_size:
            batches = [batch_size] * int(total_count / batch_size)
            batches.append(total_count % batch_size)
        else:
            batches = [total_count]

        count = 0
        for size in batches:
            count += size
            genres = factory_manager.build_batch(
                size,
                **factory_options,
            )

            try:
                manager.objects.bulk_create(
                    genres,
                    ignore_conflicts=True,
                    batch_size=batch_size
                )
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(e))

            print("Processed %s / %s" % (count, total_count))

        if kwargs.get('interval', None):
            kwargs['interval'].max = self.get_max_pk_id(manager)

        print("Finish processing %s" % manager.__name__)

        return True

    def handle(self, *args, **options):
        person_interval = PersonInterval()
        self.fillin_catalog(
            PersonFactory,
            Person,
            interval=person_interval,
            total_count=options['count_persons']
        )

        person_interval.normalize()

        genre_interval = GenreInterval()
        self.fillin_catalog(
            GenreFactory,
            Genre,
            interval=genre_interval,
            total_count=options['count_genres']
        )

        genre_interval.normalize()

        type_movie = MovieTypeFactory(name='фильм')
        type_show = MovieTypeFactory(name='сериал')

        movie_interval = MovieInterval()
        self.fillin_catalog(
            MovieFactory,
            Movie,
            interval=movie_interval,
            factory_params=dict(
                type=type_movie
            ),
            total_count=options['count_movies']
        )

        movie_interval_show = MovieInterval()
        self.fillin_catalog(
            MovieFactory,
            Movie,
            interval=movie_interval_show,
            factory_params=dict(
                type=type_show
            ),
            total_count=int(options['count_movies'] / 5)
        )

        movie_interval.max = movie_interval_show.max

        actor = PersonRoleFactory(name='актёр')
        director = PersonRoleFactory(name='директор')
        writer = PersonRoleFactory(name='сценарист')

        mp_count = options['movie_actor_coeff']*options['count_movies']
        self.fillin_catalog(
            MoviePersonRoleRandomFactory,
            MoviePersonRole,
            factory_intervals=[person_interval, movie_interval],
            factory_params=dict(
                person_role=actor
            ),
            total_count=mp_count,
        )

        mp_count = options['movie_director_coeff']*options['count_movies']
        self.fillin_catalog(
            MoviePersonRoleRandomFactory,
            MoviePersonRole,
            factory_intervals=[person_interval, movie_interval],
            factory_params=dict(
                person_role=director
            ),
            total_count=mp_count,
        )

        mp_count = options['movie_writer_coeff']*options['count_movies']
        self.fillin_catalog(
            MoviePersonRoleRandomFactory,
            MoviePersonRole,
            factory_intervals=[person_interval, movie_interval],
            factory_params=dict(
                person_role=writer
            ),
            total_count=mp_count,
        )

        mg_count = options['movie_genre_coeff']*options['count_movies']
        self.fillin_catalog(
            MovieGenreRandomFactory,
            MovieGenre,
            factory_intervals=[genre_interval, movie_interval],
            total_count=mg_count,
        )

        self.stdout.write(self.style.SUCCESS('Success'))
