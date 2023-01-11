from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, User, Group


class PostsURLTests(TestCase):

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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""

        templates_url_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group', kwargs={'slug': self.group.slug}):
                HTTPStatus.OK,
            reverse('posts:profile', kwargs={'username': self.user.username}):
                HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }

        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_redirect_anonymous(self):
        """Страница перенаправляет анонимного пользователя."""

        templates_url_names = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                reverse('users:login') + '?next='
                + reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            reverse('posts:post_create'):
                reverse('users:login') + '?next='
                + reverse('posts:post_create'),
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}):
                        reverse('users:login') + '?next='
                        + reverse('posts:add_comment',
                                  kwargs={'post_id': self.post.pk}),
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}):
                        reverse('users:login') + '?next='
                        + reverse('posts:profile_follow',
                                  kwargs={'username': self.user.username}),
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username}):
                        reverse('users:login') + '?next='
                        + reverse('posts:profile_unfollow',
                                  kwargs={'username': self.user.username})
        }

        for address, redirect_address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, redirect_address)

    def test_urls_authentificated(self):
        """Страницы доступные зарегистрированным пользователям"""

        templates_url_names = {
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                HTTPStatus.OK,
        }

        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    status
                )

    def test_edit_post_other_author(self):
        """ Страница перенапрвляет гостя """

        new_user = User.objects.create_user(username='new_auth')
        authorized_client = Client()
        authorized_client.force_login(new_user)

        response = authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )

        self.assertEqual(
            response.url,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_status_redirect_guest(self):
        """Страница перенаправляет гостя"""

        new_user = User.objects.create_user(username='new_auth')
        authorized_client = Client()
        authorized_client.force_login(new_user)

        response = authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        cache.clear()

        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            'not_found': 'core/404.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
