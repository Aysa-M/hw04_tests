from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )


    def test_models_have_correct_object_names(self):
        """
        Проверяем корректность работы метода __str__
        у моделей Post и Group.
        """
        post = PostModelTest.post
        group = PostModelTest.group
        post_field_verboses = {
            'author': 'Автор',
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
        }
        for field, expected_value in post_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                    )
        verbose_title = group._meta.get_field('title').verbose_name
        verbose_slug = group._meta.get_field('slug').verbose_name
        verbose_description = group._meta.get_field('description').verbose_name
        group_field_verboses = {
            'title': verbose_title,
            'slug': verbose_slug,
            'description': verbose_description,
        }
        for field, expected_value in group_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                    )

    def test_models_have_correct_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text_post = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_text_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
