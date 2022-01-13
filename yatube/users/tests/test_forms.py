from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

User = get_user_model()
abstract_post = settings.ABSTRACT_CREATED_POST_FOR_TESTS


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_form(self):
        """
        Проверка создания нового пользователя в базе данных
        при отправке валидной формы со страницы signup.
        """
        user_count = User.objects.count()
        form_signup = {
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
            'username': 'VaPup',
            'email': 'pupkinvasya@mail.ru',
            'password1': 'BonjornO_2021',
            'password2': 'BonjornO_2021',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_signup,
            follow=True)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + abstract_post)
        self.assertTrue((
            User.objects.filter(username='VaPup').exists()))
