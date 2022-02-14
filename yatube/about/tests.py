from audioop import reverse
from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_AboutAuthorPage(self):
        response = self.guest_client.get(reverse('/about/author/'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_AboutTechPage(self):
        response = self.guest_client.get(reverse('/about/tech/'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
