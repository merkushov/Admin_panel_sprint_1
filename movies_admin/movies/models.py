from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Certificate(TimeStampedModel):
    name = models.CharField(_('название'), max_length=60)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('возрастной ценз')
        verbose_name_plural = _('возрастные цензы')
        db_table = 'content\".\"certificates'

    def __str__(self):
        return self.name


class Genre(TimeStampedModel):
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = 'content\".\"genres'

    def __str__(self):
        return self.name


class Gender(models.TextChoices):
    MALE = 'male', _('мужской')
    FEMALE = 'female', _('женский')


class Person(TimeStampedModel):
    full_name = models.CharField(_('ФИО'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)
    gender = models.TextField(_('пол'), choices=Gender.choices, null=True)

    class Meta:
        verbose_name = _('персона')
        verbose_name_plural = _('персоны')
        db_table = 'content\".\"persons'

    def __str__(self):
        return self.full_name


class MovieType(TimeStampedModel):
    name = models.CharField(_('название'), max_length=255)

    class Meta:
        verbose_name = _('тип кинопроизведения')
        verbose_name_plural = _('типы кинопроизведений')
        db_table = 'content\".\"movie_types'

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    imdb_identifier = models.CharField(
        _('IMDB идентификатор'),
        max_length=255,
        blank=True
    )
    creation_date = models.DateField(
        _('дата создания фильма'),
        blank=True,
        null=True
    )
    file_path = models.FileField(
        _('файл'),
        upload_to='movies/',
        blank=True
    )
    rating = models.FloatField(
        _('рейтинг'),
        validators=[MinValueValidator(0)],
        blank=True,
        default=0
    )
    type = models.ForeignKey(
        MovieType,
        verbose_name=_('тип кинопроизведения'),
        related_name='movies',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    certificate = models.ForeignKey(
        Certificate,
        verbose_name=('возрастной ценз'),
        related_name='movies',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    genres = models.ManyToManyField(Genre)
    persons = models.ManyToManyField(
        Person,
        verbose_name=_('персона фильма'),
        # verbose_name_plural=_('персоны фильма'),
        # on_delete=models.CASCADE,
        blank=True,
    )

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        db_table = 'content\".\"movies'

    def __str__(self):
        return self.title


class PersonRole(TimeStampedModel):
    name = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('роль')
        verbose_name_plural = _('роли')
        db_table = 'content\".\"person_roles'

    def __str__(self):
        return self.name


class MoviePersonRole(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    person_role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    created = models.DateTimeField(
        _('дата создания'),
        auto_now_add=True,
        blank=True
    )

    class Meta:
        verbose_name = _('персона фильма')
        verbose_name_plural = _('персоны фильмов')
        db_table = 'content\".\"movie_person_role'
