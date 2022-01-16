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
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста для models.',
            author=cls.user,
            group=cls.group,
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у моделей Post корректно работает __str__."""
        post = PostModelTest.post
        verbose_author = post._meta.get_field('author').verbose_name
        verbose_text = post._meta.get_field('text').verbose_name
        verbose_pub_date = post._meta.get_field('pub_date').verbose_name
        verbose_group = post._meta.get_field('group').verbose_name
        post_field_verboses = {
            'author': verbose_author,
            'text': verbose_text,
            'pub_date': verbose_pub_date,
            'group': verbose_group,
        }
        for field, expected_value in post_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у моделей Group корректно работает __str__."""
        group = PostModelTest.group
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
        help_text_for_text = post._meta.get_field('text').help_text
        help_text_for_group = post._meta.get_field('group').help_text
        field_help_text_post = {
            'text': help_text_for_text,
            'group': help_text_for_group,
        }
        for field, expected_value in field_help_text_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
