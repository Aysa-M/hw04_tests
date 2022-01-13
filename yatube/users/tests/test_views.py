from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersViewsTests(TestCase):
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

    def test_views_users_names_namespace(self):
        """
        Проверка правильности используемых name:namespaces
        в html-шаблонах users.
        """
        users_names_namespaces = {
            'users/signup.html': reverse('users:signup'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form')
        }
        for template, reverse_name in users_names_namespaces.items():
            with self.subTest(reverse_name=reverse_name):
                if self.authorized_client:
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)
                else:
                    response = self.guest_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_views_users_signup_context(self):
        """
        Проверка соответствия формы создания поста, ожиданиям словаря context,
        передаваемого в шаблон signup.html при вызове.
        """
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
