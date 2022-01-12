from django.contrib.auth import get_user_model
from django.db import models
from .validators import validate_not_empty

User = get_user_model()
SYMBOLS_OF_POST = 15


class Post(models.Model):
    """
    Класс Post используется для создания моделей Post
    (пост в социальной сети).
    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
        max_length=10000,
        validators=[validate_not_empty],
        blank=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='postsin',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )

    class Meta:
        """
        Внутренний класс Meta для хранения метаданных
        класса Post.
        """
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:SYMBOLS_OF_POST]


class Group(models.Model):
    """
    Класс Group используется для создания моделей Group
    сообществ, в которых происходит размещение постов
    в социальной сети.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title
