from http import HTTPStatus
import shutil
import tempfile

from django.urls import reverse
from django.test import TestCase, Client
from django.conf import settings

from ..models import Post, Group, User, Comment
from .helpers import new_image

COUNT_NEW_POST = 1
COUNT_NEW_COMMENT = 1
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
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
            image=new_image()
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''Проверка создания поста'''

        posts = set(Post.objects.all())

        form_data = {
            'text': 'Текст записанный в форму',
            'group': self.group.id,
            'image': new_image()
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        posts = list(set(Post.objects.all()).difference(posts))

        self.assertEqual(len(posts), COUNT_NEW_POST)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        new_post = response.context['page_obj'].object_list[0]
        post_text = {
            posts[0].author: new_post.author,
            posts[0].group: new_post.group,
            posts[0].pub_date: new_post.pub_date,
            posts[0].text: new_post.text,
            posts[0].id: new_post.id,
            posts[0].image: new_post.image,
        }

        for field, value in post_text.items():
            self.assertEqual(field, value)

    def test_edit_post(self):
        '''Проверка редактирования поста'''

        posts_count = Post.objects.count()

        group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new-test-group'
        )

        form_data = {
            'text': 'Текст записанный в форму',
            'group': group.id,
            'iamge': new_image()
        }

        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        new_post_count = Post.objects.count()

        edit_post = Post.objects.get(id=self.post.id)

        self.assertEqual(new_post_count, posts_count)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])
        self.assertEqual(edit_post.author, self.post.author)

    def test_create_comment(self):
        '''Проверка создания комментария'''

        comments = set(Comment.objects.all())

        form_data = {
            'text': 'Комментарий записанный в форму',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        comments = list(set(Comment.objects.all()).difference(comments))

        self.assertEqual(len(comments), COUNT_NEW_COMMENT)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        new_comment = response.context['comments'][0]

        comment_text = {
            comments[0].author_id: new_comment.author.id,
            comments[0].created: new_comment.created,
            comments[0].text: new_comment.text,
            comments[0].id: new_comment.id,
            comments[0].post_id: new_comment.post.id,
        }

        for field, value in comment_text.items():
            self.assertEqual(field, value)
