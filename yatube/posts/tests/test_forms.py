from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()
CREATION_DATE = timezone.now()


class PostsFormsTests(TestCase):
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
            author=cls.user,
            text='Тестовая группа. 1',
            group=cls.group,
        )
        cls.form = PostForm()
        cls.author = cls.user.username

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
            'author': self.author,
            'pub_date': CREATION_DATE,
            }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.author})
            )
        self.assertEqual(Post.objects.count(), post_count+1)
        self.assertTrue((
            Post.objects.filter(
                text='Post in da home',
                group=self.group_second)
                ).exists())

    def test_form_posts_edit_post(self):
        """
        Проверка изменения существующего поста в базе данных при
        отправке валидной формы со страницы редактирования
        поста.
        """
        post_count = Post.objects.count()
        if self.post.author == self.authorized_client:
            form_data_edit = {
                'text': 'Тестовая группа 2.',
                'group': self.group_second.pk,
                'author': self.author,
                'pub_date': CREATION_DATE,
            }
            response = self.authorized_client.post(
                reverse('posts:post_edit'),
                kwargs={'post_id': '1'},
                data=form_data_edit,
                follow=True)
            self.assertRedirects(response, reverse('posts:post_detail', kwargs={'post_id': '1'}))
            self.assertEqual(Post.objects.count(), post_count)
            self.assertTrue((
                Post.objects.filter(
                    text='Тестовая группа 2.',
                    slug='test-slug-second')
                    ).exists())

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
        self.assertTrue(group_help_texts, 'Группа, к которой будет относиться пост')
            