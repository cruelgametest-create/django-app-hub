import json

from django.test import TestCase, Client
from django.urls import reverse


class GetCookieViewTestCase(TestCase):
    ua = Client(HTTP_USER_AGENT="Mozilla/5.0")

    def test_get_cookie_view(self):
        response = self.ua.get(reverse("myauth:cookie-get"))
        self.assertContains(response, "Cookie value")


class FooBarViewTest(TestCase):
    ua = Client(HTTP_USER_AGENT="Mozilla/5.0")

    def test_foo_bar_view(self):
        response = self.ua.get(reverse("myauth:foo-bar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        expected_data = {"foo": "bar", "spam": "eggs"}
        self.assertJSONEqual(response.content, expected_data)
