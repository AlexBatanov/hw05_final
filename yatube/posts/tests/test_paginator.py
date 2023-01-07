from django.urls import reverse
from django.test import TestCase, Client

from ..models import Group, Post, User
from ..constants import POSTS_LIMIT

COUNT_POSTS_PAGE_TWO = 3


class PaginatorTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа где в названии больше 15 символов',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(POSTS_LIMIT + COUNT_POSTS_PAGE_TWO):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост где в названии больше 15 символов {i}',
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_first_page_context_guest_client(self):
        '''Проверка количества постов на первой странице. '''

        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_LIMIT)

    def test_correct_second_page_context_guest_client(self):
        '''Проверка количества постов на второй страницае. '''

        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 COUNT_POSTS_PAGE_TWO)
