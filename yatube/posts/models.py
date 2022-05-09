from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('Текст ссылки', unique=True)
    description = models.TextField('Описание группы')

    class Meta:
        verbose_name = "Администрирование группы"
        verbose_name_plural = "Администрирование групп"

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        verbose_name = "Администрирование поста"
        verbose_name_plural = "Администрирование постов"
        ordering = ("-pub_date", )

    def __str__(self) -> str:
        return self.text[:15]
