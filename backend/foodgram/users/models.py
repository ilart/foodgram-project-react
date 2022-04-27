import enum

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

ROLES = (
    ('user', 'Аутентифицированный пользователь'),
    ('admin', 'Администратор')
)


class User(AbstractUser):
    class Roles(enum.Enum):
        user = 'user'
        moderator = 'moderator'
        admin = 'admin'

    role = models.CharField(
        'Роль',
        choices=ROLES,
        default='user',
        max_length=32
    )
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[\w.@+-]+\Z'
            )
        ]
    )

    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['pk']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.Roles.admin.value

    @property
    def is_user(self):
        return self.role == self.Roles.user.value

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписчик',
        blank=True,
        null=True,
    )

    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscribing', 'user'],
                name='subscribe_unique'
            ),
        ]

    def __str__(self):
        return f'{self.user} -> {self.subscribing}'
