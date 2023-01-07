from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import User


class AboutURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""

        templates_url_names = {
            '/about/author/': {'status': HTTPStatus.OK},
            '/about/tech/': {'status': HTTPStatus.OK},
        }

        for address, value in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, value['status'])

    def test_urls_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
