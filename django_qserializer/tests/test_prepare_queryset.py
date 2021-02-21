import pytest

from django_qserializer import BaseSerializer
from django_qserializer.tests.testapp.models import Author, Book


@pytest.fixture
def book_fixture(db):
    author = Author.objects.create()
    return Book.objects.create(author=author)


def test_manager_works(book_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        pass

    book = Book.objects.to_serialize(S).first()
    with django_assert_num_queries(1):
        book.author


def test_select_related_attr(book_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        select_related = ['author']

    book = Book.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        book.author


def test_prefetch_related_attr(book_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        prefetch_related = ['author']

    with django_assert_num_queries(2):
        # book query + author prefetch query
        book = Book.objects.to_serialize(S).first()

    with django_assert_num_queries(0):
        book.author
