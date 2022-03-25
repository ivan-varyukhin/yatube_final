from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Текст сообщения'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор сообщения',
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа',
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Сообщение',
        help_text='Сообщение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор'
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата комментария',
        help_text='Дата комментария',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             verbose_name='Подписчик',
                             help_text='Подписчик',
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='Автор',
                               help_text='Автор',
                               related_name='following')

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(fields=('user', 'author', ),
                             name="unique_subscriber"),
        )

    def __str__(self):
        return self.user.username+' follow '+self.author.username
