from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_LEN_TITLE

User = get_user_model()


class Group(models.Model):
    '''
    Создает модель группы

    Atributes:
        title - название группы с ограничением в 200 символов;
        slug - уникальное поле для создания читаемого URL;
        description - описание группы.
    '''

    title = models.CharField(max_length=200, verbose_name='название группы')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='описание группы')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        '''Возвращает название группы'''

        return self.title[:MAX_LEN_TITLE]


class Post(models.Model):
    '''
    Создает модель поста

    Atributes:
        text - текст поста;
        pub_date - автоматом создается дата при создании поста;
        author - ключ для связей Many to One;
        group - ключ для связей Many to One;
        image - поле для картинки.
    '''

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        '''Возвращает название группы'''

        return self.text[:MAX_LEN_TITLE]


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    text = models.TextField(
        verbose_name='Текст комментария',
    )

    created = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']

    def __str__(self) -> str:
        return self.text[:MAX_LEN_TITLE]


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользоваетль'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique'),
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписчики'

    def __str__(self) -> str:
        return f'{self.user.username} - {self.author.username}'
