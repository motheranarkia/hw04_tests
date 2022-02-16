from audioop import reverse
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_list = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        )

    def test_url_exists_at_desired_location(self):
        for url in self.__class__.url_list:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)
