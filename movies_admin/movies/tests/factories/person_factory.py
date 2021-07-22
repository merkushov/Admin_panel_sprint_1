import factory
from faker import Faker

fake = Faker(['ru_RU'])
Faker.seed(0)


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'movies.Person'

    full_name = factory.Sequence(lambda _: fake.name_nonbinary())
    birth_date = factory.Sequence(lambda _: fake.date())
    gender = factory.Sequence(
        lambda _: fake.word(ext_word_list=['male', 'female'])
    )
