from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostsViewTests(TestCase):
    """
    Класс для создания тестов для проверки работы view функций
    приложения posts.
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
            text='Текст тестового поста для Views.',
            author=cls.user,
            group=cls.group,
        )
        cls.objs = []
        for i in range(2, 15):
            cls.objs.append((
                Post(
                    author=cls.user,
                    group=cls.group,
                    text='Создание поста {i} ранжированием.'.format(i=i)))
            )
        cls.page_obj = Post.objects.bulk_create(cls.objs)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_names_namespace(self):
        """
        Проверка о том, что во view-функциях используются правильные
        html-шаблоны (name:namespace).
        """
        posts_names_namespaces = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in posts_names_namespaces.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def first_object_context(self, *args, **kwargs) -> dict:
        """
        Возвращает context словарь первого элемента списка
        page_obj для последующего использования в сравнительных тестах
        context страниц.
        """
        first_object = self.page_obj[0]
        first_object_context = {
            'pk': first_object.pk,
            'text': first_object.text,
            'pub_date': first_object.pub_date,
            'author': first_object.author,
            'username': first_object.author.username,
            'group': first_object.group,
            'title': first_object.group.title,
            'slug': first_object.group.slug,
        }
        return first_object_context

    def test_views_posts_index_context(self):
        """
        Проверка соответствия списка постов ожиданиям словаря context,
        передаваемого в шаблон index.html при вызове.
        """
        response = self.client.get(reverse('posts:index'))
        first_object_index = self.first_object_context(response)
        self.assertEqual(first_object_index['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_index['text'], self.page_obj[0].text)
        self.assertEqual(first_object_index['pub_date'],
                         self.page_obj[0].pub_date)

    def test_views_posts_group_list_context(self):
        """
        Проверка соответствия списка постов, отфильрованного по группе
        ожиданиям словаря context, передаваемого в шаблон
        group_list.html при вызове.
        """
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object_group_list = self.first_object_context(response)
        self.assertEqual(first_object_group_list['author'],
                         self.page_obj[0].author)
        self.assertEqual(
            first_object_group_list['text'],
            self.page_obj[0].text)
        self.assertEqual(first_object_group_list['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_group_list['group'],
                         self.page_obj[0].group)
        self.assertEqual(first_object_group_list['title'],
                         self.page_obj[0].group.title)
        self.assertEqual(first_object_group_list['slug'],
                         self.page_obj[0].group.slug)

    def test_views_posts_profile_context(self):
        """
        Проверка соответствия списка постов, отфильтрованного по пользователю,
        ожиданиям словаря context, передаваемого в шаблон profile.html
        при вызове.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object_profile = self.first_object_context(response)
        self.assertEqual(first_object_profile['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_profile['username'],
                         self.page_obj[0].author.username)
        self.assertEqual(first_object_profile['text'], self.page_obj[0].text)
        self.assertEqual(first_object_profile['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_profile['group'],
                         self.page_obj[0].group)

    def test_views_posts_post_detail_context(self):
        """
        Проверка соответствия одного поста, отфильтрованного по id поста,
        ожиданиям словаря context, передаваемого в шаблон
        post_detail.html при вызове.
        """
        response = self.client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_object_post = self.first_object_context(response)
        self.assertEqual(first_object_post['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_post['username'],
                         self.page_obj[0].author.username)
        self.assertEqual(first_object_post['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_post['text'], self.page_obj[0].text)
        self.assertEqual(first_object_post['group'],
                         self.page_obj[0].group)
        self.assertEqual(first_object_post['pk'],
                         self.page_obj[0].pk)

    def test_views_posts_edit_post_context(self):
        """
        Проверка соответствия формы редактирования поста, отфильтрованного по
        id поста, ожиданиям словаря context, передаваемого
        в шаблон create_post.html при вызове.
        """
        if self.post.author == self.authorized_client:
            response = self.authorized_client.get(
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.pk})
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
                    'text': self.post.text,
                    'group': self.group.pk,
                }
                response = self.authorized_client.post(
                    reverse('posts:post_create',
                            data=form_data,
                            follow=True))
                self.assertRedirects(response, 'posts:post_detail')
                pages_for_post = [
                    '/',
                    '/posts/group/{slug}/'.format(slug=self.group.slug),
                    '/profile/{username}/'.format(username=self.user.username),
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)
            elif self.post.group != self.group:
                form_data = {
                    'text': self.post.text,
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
                    '/profile/{username}/'.format(username=self.user.username),
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)
