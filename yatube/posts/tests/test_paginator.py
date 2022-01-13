from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()
FIRST_PAGE_COUNT = 10
SECOND_PAGE_COUNT = 3


class PaginatorViewsTest(TestCase):
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
        cls.objs = []
        for i in range(1, 14):
            cls.objs.append((
                Post(
                    pk=i,
                    author=cls.user,
                    group=cls.group,
                    text='Тестовая группа.'
                )))
        cls.post_obj = Post.objects.bulk_create(cls.objs)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_another = Client()
        self.authorized_client_another.force_login(self.user_second)

    def test_first_page_index_contains_ten_records(self):
        """
        Проверка паджинатора - вывод десяти постов на
        первую страницу index.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(reverse(
                'posts:index'))
            self.assertEqual(
                len(response.context['page_obj']), FIRST_PAGE_COUNT)
        else:
            response = self.guest_client.get(
                reverse('posts:index'))
            self.assertEqual(
                len(response.context['page_obj']), FIRST_PAGE_COUNT)

    def test_second_page_index_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних трех постов на
        вторую страницу index.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(
                reverse('posts:index') + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), SECOND_PAGE_COUNT)
        else:
            response = self.guest_client.get(
                reverse('posts:index') + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), SECOND_PAGE_COUNT)

    def test_first_page_group_list_contains_ten_records(self):
        """
        Проверка паджинатора - вывод десяти постов на
        первую страницу group_list.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}))
            self.assertEqual(
                len(response.context['page_obj']), FIRST_PAGE_COUNT)
        else:
            response = self.guest_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}))
            self.assertEqual(
                len(response.context['page_obj']), FIRST_PAGE_COUNT)

    def test_second_page_group_list_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних трех постов на
        вторую страницу group_list.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get((reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'})) + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), SECOND_PAGE_COUNT)
        else:
            response = self.guest_client.get((reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'})) + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), SECOND_PAGE_COUNT)

    def test_first_page_profile_contains_ten_records(self):
        """
        Проверка паджинатора - вывод десяти постов на
        первую страницу profile.html.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}))
        self.assertEqual(
            len(response.context['page_obj']), FIRST_PAGE_COUNT)

    def test_second_page_profile_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних трех постов на
        вторую страницу group_list.html.
        """
        response = self.authorized_client.get((reverse(
            'posts:profile',
            kwargs={'username': 'auth'})) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), SECOND_PAGE_COUNT)
