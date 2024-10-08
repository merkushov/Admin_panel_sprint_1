from django.contrib import admin
from .models import (
    Movie, Genre, MovieType, Person,
    PersonRole, MoviePersonRole, Certificate,
    MovieGenre
)


class MoviePersonRoleInline(admin.TabularInline):
    model = MoviePersonRole
    extra = 0


class MovieGenreInline(admin.TabularInline):
    model = MovieGenre


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'type', 'created', 'rating')

    # фильтрация в списке
    list_filter = ('type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'creation_date', 'description', 'certificate',
        'file_path', 'rating'
    )

    inlines = (MovieGenreInline, MoviePersonRoleInline)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(MovieType)
class MovieTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (MoviePersonRoleInline, )


@admin.register(PersonRole)
class PersonRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    pass
