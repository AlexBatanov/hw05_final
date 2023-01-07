import shutil

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, User, Group, Comment, Follow
from ..forms import PostForm
from .test_forms import TEMP_MEDIA_ROOT
from .create_image import new_image


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug_2',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=new_image()
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def cheking_attributes(self, first_object):

        post_text = {
            first_object.author: self.user,
            first_object.group: self.group,
            first_object.pub_date: self.post.pub_date,
            first_object.text: self.post.text,
            first_object.id: self.post.id,
            first_object.image: self.post.image
        }

        for field, value in post_text.items():
            self.assertEqual(field, value)

    def test_namespase_correct_template(self):
        """Применяется праильный шаблон для пространства имен."""

        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': f'{self.user.username}'}
                )
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
            'posts/group_list.html': (
                reverse('posts:group', kwargs={'slug': f'{self.group.slug}'})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        cache.clear()

        response = self.authorized_client.get(reverse('posts:index'))

        first_object = response.context['page_obj'].object_list[0]

        self.cheking_attributes(first_object)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse(
                'posts:group',
                kwargs={'slug': f'{self.group.slug}'}
            )
        )

        first_object = response.context['page_obj'].object_list[0]

        self.cheking_attributes(first_object)

        self.assertEqual(response.context['group'], self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )

        first_object = response.context['page_obj'].object_list[0]

        self.cheking_attributes(first_object)

        self.assertEqual(response.context['author'], self.post.author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

        first_object = response.context['post']
        self.assertEqual(self.post, first_object)

        self.cheking_attributes(first_object)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_edit_show_correct_context(self):
        """
        Шаблон post_create для редактирования
        сформирован с правильным контекстом.
        """

        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )

        self.assertTrue(response.context['is_edit'])
        self.assertEqual(self.post, response.context['form'].instance)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_added_correct(self):
        '''Корретное добовления нового поста'''

        post = Post.objects.create(
            text='Тестовый текст 2',
            author=self.user,
            group=self.group)

        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                first_post = response.context['page_obj'].object_list[0]
                self.assertEqual(post, first_post)

    def test_absence_post_someone_else_pages(self):
        '''
        Корретное не отображение нового поста
        на чужих страницах
        '''

        user = User.objects.create_user(username='auth_new')

        post = Post.objects.create(
            text='Тестовый пост новго автора',
            author=user,
            group=self.group_2
        )
        pages = [
            reverse('posts:group', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                posts = response.context['page_obj']
                self.assertNotIn(post, posts)

    def test_added_comment(self):
        '''Корретное добовления нового комментария'''

        comment = Comment.objects.create(
            text='test comment',
            author=self.user,
            post=self.post
        )

        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )

        comments = response.context['comments']
        self.assertIn(comment, comments)

    def test_cahe(self):
        """Корректная работа кеша"""

        response = self.client.get(reverse('posts:index'))
        Post.objects.get(id=self.post.id).delete()
        new_response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, new_response.content)

    def test_subscriptions_per_user(self):
        """Корректная подписка на других пользователей"""

        user = User.objects.create_user(username='authnew')
        authorized_client = Client()
        authorized_client.force_login(user)

        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{self.user.username}'}
            )
        )

        response = authorized_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj'].object_list
        self.assertIn(self.post, posts)

    def test_unsubscribe_per_user(self):
        """Корректная отписка от пользователя"""

        user = User.objects.create_user(username='auth_new')
        authorized_client = Client()
        authorized_client.force_login(user)

        Follow.objects.create(
            user=user,
            author=self.user
        )

        authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{self.user.username}'}
            )
        )

        response = authorized_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertNotIn(self.post, posts)

    def test_subscriber_has_new_post(self):
        """Корректное отображение нового поста у подписчика"""

        user = User.objects.create_user(username='auth_new')
        authorized_client = Client()
        authorized_client.force_login(user)

        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{self.user.username}'}
            )
        )

        response = authorized_client.get(reverse('posts:follow_index'))
        old_count_post = len(response.context['page_obj'].object_list)

        Post.objects.create(
            text='Тестовый текст 2',
            author=self.user,
            group=self.group
        )

        response = authorized_client.get(reverse('posts:follow_index'))
        new_count_post = len(response.context['page_obj'].object_list)

        self.assertEquals(old_count_post + 1, new_count_post)

    def test_subscriber_has_new_post(self):
        """Корректное не отображение нового поста у тех кто не подписан"""

        user = User.objects.create_user(username='auth_new')
        authorized_client = Client()
        authorized_client.force_login(user)

        post = Post.objects.create(
            text='Тестовый текст 2',
            author=self.user,
            group=self.group
        )

        response = authorized_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj'].object_list
        self.assertNotIn(post, posts)
