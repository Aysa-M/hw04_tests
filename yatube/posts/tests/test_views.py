from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_second = User.objects.create_user(username='LordWeider')
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
            author=cls.user,
            text='Тестовая группа. 1',
            group=cls.group,
        )
        cls.objs = []
        for i in range(2, 15):
            cls.objs.append((
                Post(
                    pk=i,
                    author=cls.user,
                    group=cls.group,
                    text='Тестовая группа.'))
            )
        cls.post_list = Post.objects.bulk_create(cls.objs)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_second = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_second.force_login(self.user_second)

    def test_views_names_namespace(self):
        """
        Проверка о том, что во view-функциях используются правильные
        html-шаблоны (name:namespace).
        """
        posts_names_namespaces = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}): 'posts/create_post.html',
        }
        for reverse_name, template in posts_names_namespaces.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_posts_index_context(self):
        """
        Проверка соответствия списка постов ожиданиям словаря context,
        передаваемого в шаблон index.html при вызове.
        """
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_text_0, 'Тестовая группа.')

    def test_views_posts_group_list_context(self):
        """
        Проверка соответствия списка постов, отфильрованного по группе
        ожиданиям словаря context, передаваемого в шаблон
        group_list.html при вызове.
        """
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)

    def test_views_posts_profile_context(self):
        """
        Проверка соответствия списка постов, отфильтрованного по пользователю,
        ожиданиям словаря context, передаваемого в шаблон profile.html
        при вызове.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        self.assertEqual(post_author_0, self.user)

    def test_views_posts_post_detail_context(self):
        """
        Проверка соответствия одного поста, отфильтрованного по id поста,
        ожиданиям словаря context, передаваемого в шаблон
        post_detail.html при вызове.
        """
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(response.context['post_profile'].pk, self.post.pk)

    def test_views_posts_edit_post_context(self):
        """
        Проверка соответствия формы редактирования поста, отфильтрованного по
        id поста, ожиданиям словаря context, передаваемого в шаблон
        create_post.html при вызове.
        """
        if self.post.author == self.authorized_client:
            response = self.authorized_client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': '1'})
            )
            form_fields_edit = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields_edit.items():
                while self.subTest(value=value):
                    form_field_edit = response.context.get('form').fields.get(
                        value)
                    self.assertIsInstance(form_field_edit, expected)

    def test_views_posts_create_post_context(self):
        """
        Проверка соответствия формы создания поста,
        ожиданиям словаря context, передаваемого в шаблон
        create_post.html при вызове.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_posts_created_post_is_arised_on_pages_context(self):
        """
        Проверка отображения поста на: главной странице сайта,
        странице выбранной группы и в профайле пользователя в случае,
        если что если при создании поста указать группу. Данный пост
        не должен попасть в группу, для которой он не был предназначен.
        """
        if self.post.author == self.authorized_client:
            if self.post.group == self.group:
                form_data = {
                    'text': 'Тестовая группа. 1',
                    'group': self.group.pk,
                }
                response = self.authorized_client.post(
                    reverse(
                        'posts:post_create',
                        data=form_data,
                        follow=True)
                )
                self.assertRedirects(response, reverse('posts:post_detail'))
                pages_for_post = [
                    '/',
                    '/posts/group/test-slug/',
                    '/profile/auth/',
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)
            elif self.post.group != self.group:
                form_data = {
                    'text': 'Тестовая группа. 1',
                    'group': '',
                }
                response = self.authorized_client.post(
                    reverse(
                        'posts:post_create',
                        data=form_data,
                        follow=True))
                self.assertRedirects(response, reverse('posts:post_detail'))
                self.assertFormError(
                    response,
                    'form',
                    'group',
                    'Созданный пост не будет перенаправлен'
                    'на страницу group_list'
                )
                pages_for_post = [
                    '/',
                    '/profile/auth/',
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)
