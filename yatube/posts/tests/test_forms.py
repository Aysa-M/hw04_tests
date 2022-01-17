from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()
ABSTRACT_OBJECT = settings.ABSTRACT_CREATED_OBJECT_FOR_TESTS


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_second = User.objects.create_user(username='Aysa')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_second = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-second',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста для forms.',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.profile_username = cls.user.username

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user_second)

    def test_form_posts_create_post(self):
        """
        Проверка создания новой записи в базе данных
        при отправке валидной формы со страницы создания данного
        поста.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Post in da home',
            'group': self.group_second.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.profile_username})
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + ABSTRACT_OBJECT)
        ordered_posts = Post.objects.order_by('id')
        last_post = ordered_posts.last()
        self.assertEqual(form_data['text'], last_post.text)
        self.assertEqual(form_data['group'], last_post.group.pk)

    def test_form_posts_edit_post(self):
        """
        Проверка изменения существующего поста в базе данных при
        отправке валидной формы со страницы редактирования
        поста.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms.',
            'group': self.group_second.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=True,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(form_data_edit['text'],
                         edited_post.text)
        self.assertEqual(form_data_edit['group'],
                         edited_post.group.pk)

    def test_form_posts_edit_post_by_not_author(self):
        """
        Проверка невозможности изменения существующего поста
        в базе данных при отправке валидной формы со страницы редактирования
        поста незарегистрированным пользователем.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms не автором.',
            'group': self.group_second.pk,
        }
        response = self.authorized_client_second.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=False,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не является автором поста.'
                         'Редактирование поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertNotEqual(form_data_edit['text'],
                            edited_post.text)
        self.assertNotEqual(form_data_edit['group'],
                            edited_post.group.pk)

    def test_form_posts_create_post_by_anonymous(self):
        """
        Проверка создания нового поста незарегистрированным клиентом
        в базе данных при отправке валидной формы со страницы создания данного
        поста. Пост не должен создаться.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Post by anonymous',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не зарегистрирован.'
                         'Создание поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(
            Post.objects.count(),
            post_count)

    def test_form_posts_edit_post_by_anonymous(self):
        """
        Проверка невозможности изменения существующего поста
        в базе данных при отправке валидной формы со страницы редактирования
        поста незарегистрированным пользователем.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms анонимом.',
            'group': '',
        }
        response = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=False,
            follow=False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не зарегистрирован.'
                         'Редактирование поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertNotEqual(form_data_edit['text'],
                            edited_post.text)
        self.assertNotEqual(form_data_edit['group'],
                            edited_post.group.pk)

    def test_title_label(self):
        """Проверка labels полей формы."""
        text_label = PostsFormsTests.form.fields['text'].label
        group_label = PostsFormsTests.form.fields['group'].label
        self.assertTrue(text_label, 'Текст поста')
        self.assertTrue(group_label, 'Выбрать группу')

    def test_title_help_text(self):
        """Проверка help_text полей формы."""
        text_help_texts = PostsFormsTests.form.fields['text'].help_text
        group_help_texts = PostsFormsTests.form.fields['group'].help_text
        self.assertTrue(text_help_texts, 'Текст нового поста')
        self.assertTrue(group_help_texts, 'Группа, к которой будет'
                        'относиться пост')
