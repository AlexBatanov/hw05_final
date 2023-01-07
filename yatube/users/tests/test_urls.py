from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import Group, Post, User


class UserstURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа где в названии больше 15 символов',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост где в названии больше 15 символов',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""

        templates_url_names = {
            '/auth/signup/': {'status': HTTPStatus.OK}
        }

        for address, value in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, value['status'])

    def test_urls_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
