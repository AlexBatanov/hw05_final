from django.test import TestCase, Client

from ..constants import MAX_LEN_TITLE
from ..models import Group, Post, User


class PostModelTest(TestCase):

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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        field_str = {
            self.group: self.group.title[:MAX_LEN_TITLE],
            self.post: self.post.text[:MAX_LEN_TITLE],
        }

        for field, value in field_str.items():
            with self.subTest(field=field):
                self.assertEqual(str(field), value)

    def test_verbose_name(self):
        """Проверяем, что у моделей корректный verbose_name."""

        post = PostModelTest.post

        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, value
                )

    def test_help_text(self):
        """Проверяем, что у моделей корректный help_text."""

        post = PostModelTest.post

        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, value
                )
