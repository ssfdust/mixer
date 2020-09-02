import datetime as dt

import pytest
from peewee import *


db = SqliteDatabase(":memory:")


class Person(Model):
    name = CharField()
    status = CharField(
        choices=(("user", "user"), ("moderator", "moderator"), ("admin", "admin"))
    )
    created = DateTimeField(default=dt.datetime.now)
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db


class Pet(Model):
    owner = ForeignKeyField(Person, related_name="pets")
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db


Person.create_table()
Pet.create_table()


@pytest.fixture
def mixer():
    from mixer.backend.peewee import mixer

    return mixer


@pytest.fixture(autouse=True)
def clean_tables():
    Person.delete().execute()
    Pet.delete().execute()


def test_mixer(mixer):
    person = mixer.blend(Person)
    assert person.name
    assert person.id
    assert person.birthday
    assert person.status in ("user", "moderator", "admin")

    pet = mixer.blend(Pet)
    assert pet.name
    assert pet.animal_type
    assert pet.owner

    with mixer.ctx(commit=False):
        person = mixer.blend(Person)
        assert person.id


def test_guard(mixer):
    person = mixer.blend(Person)
    person2 = mixer.guard(Person.name == person.name).blend(Person)
    assert person.id == person2.id


def test_reload(mixer):
    person = mixer.blend(Person, name="true")
    person.name = "wrong"

    person = mixer.reload(person)
    assert person.name == "true"


def test_select(mixer):
    person = mixer.blend(Person)
    pet = mixer.blend(Pet, owner=mixer.SELECT)
    assert person == pet.owner
