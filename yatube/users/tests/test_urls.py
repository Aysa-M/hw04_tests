from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client({
            'username': 'Sunny',
            'password': 'smile'
        })
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location_for_guest_client(self):
        """
        Проверка доступности адресов приложения users для
        неавторизованных пользователей.
        """
        guest_client_urls = [
            '/users/signup/',
            '/users/login/',
            '/unexpected_page/',
        ]
        for address in guest_client_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if response == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_at_desired_location_for_authorized_client(self):
        """
        Проверка доступности адресов приложения users для
        авторизованных пользователей.
        """
        authorized_client_urls = [
            '/users/logout/',
            '/users/signup/',
            '/users/login/',
            '/users/password_reset_form/',
            '/users/password_reset_done/',
            '/users/password_reset_confirm/',
            '/users/password_reset_complete/',
            '/users/password_change_form/',
            '/users/password_change_done/',
            '/unexpected_page/',
        ]
        for address in authorized_client_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if response == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_templates(self):
        """URL-адрес использует соответствующие шаблоны users."""
        users_templates = {
            'users/logged_out.html': '/auth/logout/',
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_reset_form.html': '/auth/password_reset_form/',
            'users/password_reset_done.html': '/auth/password_reset_done/',
            'users/password_reset_complete.html':
            '/auth/password_reset_complete/',
        }
        for template, address in users_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
