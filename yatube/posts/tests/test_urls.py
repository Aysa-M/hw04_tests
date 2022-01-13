from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
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
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location_for_guest_client(self):
        """
        Проверка доступности адресов приложения posts для
        неавторизованных пользователей.
        """
        url_names_guest = [
            '/',
            '/posts/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
            '/unexisting_page/',
        ]
        for address in url_names_guest:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_about_url_exists_at_desired_location_for_authorized(self):
        """
        Проверка доступности адресов приложения posts для
        авторизованных пользователей.
        """
        url_names_authorized = [
            '/',
            '/posts/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
            '/posts/1/edit/',
            '/create/',
            '/unexisting_page/',
        ]
        for address in url_names_authorized:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_post_by_post_author(self):
        """
        Проверка доступности адреса редактирования поста для
        автора поста.
        """
        response = self.authorized_client.get(
            '/create/',
            args=[self.post.author]
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующие шаблоны posts."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
